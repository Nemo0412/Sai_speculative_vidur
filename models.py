"""
Core model classes for the scheduling algorithm system.
"""

import heapq
from typing import List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time


class RequestType(Enum):
    """Types of requests."""
    PREFILL = "prefill"
    DECODE = "decode"


@dataclass
class Request:
    """Represents a request from a draft model."""
    request_id: int
    draft_model_id: int
    request_type: RequestType
    arrival_time: float
    target_model_id: Optional[int] = None  # Assigned by router
    processing_time: float = 0.0  # Time to process on assigned target
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def __lt__(self, other):
        """For priority queue ordering."""
        return self.arrival_time < other.arrival_time


class TargetModel:
    """Represents a target model with its queue and batch processing capabilities."""
    
    def __init__(self, target_id: int, queue_size: int, batch_size: int):
        self.target_id = target_id
        self.queue_size = queue_size
        self.batch_size = batch_size
        self.queue: List[Request] = []
        self.current_batch: List[Request] = []
        self.batch_start_time: Optional[float] = None
        self.total_processed = 0
        self.total_processing_time = 0.0
        
    def can_accept_request(self) -> bool:
        """Check if the target can accept a new request."""
        return len(self.queue) < self.queue_size
    
    def add_request(self, request: Request) -> bool:
        """Add a request to the target's queue."""
        if not self.can_accept_request():
            return False
        
        self.queue.append(request)
        return True
    
    def get_queue_utilization(self) -> float:
        """Get current queue utilization (0.0 to 1.0)."""
        return len(self.queue) / self.queue_size
    
    def is_batch_ready(self) -> bool:
        """Check if there's a batch ready to process."""
        return len(self.current_batch) > 0
    
    def can_start_new_batch(self) -> bool:
        """Check if we can start a new batch."""
        return len(self.current_batch) == 0 and len(self.queue) > 0
    
    def start_new_batch(self, current_time: float, scheduling_algorithm: str = "shortest_job_first") -> bool:
        """Start processing a new batch of requests."""
        if not self.can_start_new_batch():
            return False
        
        # Select requests for the batch based on scheduling algorithm
        batch_requests = self._select_batch_requests(scheduling_algorithm)
        
        if not batch_requests:
            return False
        
        self.current_batch = batch_requests
        self.batch_start_time = current_time
        
        # Remove selected requests from queue
        for req in batch_requests:
            self.queue.remove(req)
        
        return True
    
    def _select_batch_requests(self, algorithm: str) -> List[Request]:
        """Select requests for the current batch based on scheduling algorithm."""
        if not self.queue:
            return []
        
        if algorithm == "shortest_job_first":
            # Sort by processing time (shortest first)
            sorted_requests = sorted(self.queue, key=lambda x: x.processing_time)
        elif algorithm == "fifo":
            # First in, first out (already sorted by arrival time)
            sorted_requests = self.queue.copy()
        elif algorithm == "priority":
            # Priority based on request type (prefill has higher priority)
            sorted_requests = sorted(self.queue, key=lambda x: (x.request_type.value, x.arrival_time))
        else:
            # Default to FIFO
            sorted_requests = self.queue.copy()
        
        # Take up to batch_size requests
        return sorted_requests[:self.batch_size]
    
    def process_batch(self, current_time: float) -> List[Request]:
        """Process the current batch and return completed requests."""
        if not self.is_batch_ready():
            return []
        
        completed_requests = []
        
        # Calculate batch processing time (max of individual request times)
        batch_processing_time = max(req.processing_time for req in self.current_batch)
        
        # Check if batch is complete
        if current_time - self.batch_start_time >= batch_processing_time:
            # Batch is complete
            for req in self.current_batch:
                req.start_time = self.batch_start_time
                req.end_time = current_time
                completed_requests.append(req)
                self.total_processed += 1
                self.total_processing_time += req.processing_time
            
            # Clear current batch
            self.current_batch = []
            self.batch_start_time = None
        
        return completed_requests
    
    def get_status(self) -> dict:
        """Get current status of the target model."""
        return {
            "target_id": self.target_id,
            "queue_length": len(self.queue),
            "queue_utilization": self.get_queue_utilization(),
            "current_batch_size": len(self.current_batch),
            "is_processing": self.is_batch_ready(),
            "total_processed": self.total_processed,
            "total_processing_time": self.total_processing_time
        }


class Router:
    """Router that distributes requests to target models."""
    
    def __init__(self, queue_size: int, target_models: List[TargetModel]):
        self.queue_size = queue_size
        self.target_models = target_models
        self.queue: List[Request] = []
        self.total_routed = 0
        self.routing_algorithm = "shortest_queue"
        
    def can_accept_request(self) -> bool:
        """Check if the router can accept a new request."""
        return len(self.queue) < self.queue_size
    
    def add_request(self, request: Request) -> bool:
        """Add a request to the router's queue."""
        if not self.can_accept_request():
            return False
        
        self.queue.append(request)
        return True
    
    def route_requests(self, current_time: float) -> int:
        """Route requests from router queue to target models."""
        routed_count = 0
        
        # Process requests in order
        requests_to_route = self.queue.copy()
        self.queue.clear()
        
        for request in requests_to_route:
            target_id = self._select_target(request)
            
            if target_id is not None:
                # Route to selected target
                if self.target_models[target_id].add_request(request):
                    request.target_model_id = target_id
                    routed_count += 1
                    self.total_routed += 1
                else:
                    # Target queue is full, put request back in router queue
                    self.queue.append(request)
            else:
                # No suitable target found, put request back in router queue
                self.queue.append(request)
        
        return routed_count
    
    def _select_target(self, request: Request) -> Optional[int]:
        """Select the best target model for a request based on routing algorithm."""
        if self.routing_algorithm == "shortest_queue":
            return self._shortest_queue_routing(request)
        elif self.routing_algorithm == "least_loaded":
            return self._least_loaded_routing(request)
        elif self.routing_algorithm == "round_robin":
            return self._round_robin_routing(request)
        else:
            return self._shortest_queue_routing(request)
    
    def _shortest_queue_routing(self, request: Request) -> Optional[int]:
        """Route to target with shortest queue."""
        available_targets = [
            (i, target) for i, target in enumerate(self.target_models)
            if target.can_accept_request()
        ]
        
        if not available_targets:
            return None
        
        # Find target with shortest queue
        best_target_id, _ = min(available_targets, key=lambda x: len(x[1].queue))
        return best_target_id
    
    def _least_loaded_routing(self, request: Request) -> Optional[int]:
        """Route to least loaded target (lowest queue utilization)."""
        available_targets = [
            (i, target) for i, target in enumerate(self.target_models)
            if target.can_accept_request()
        ]
        
        if not available_targets:
            return None
        
        # Find target with lowest queue utilization
        best_target_id, _ = min(available_targets, key=lambda x: x[1].get_queue_utilization())
        return best_target_id
    
    def _round_robin_routing(self, request: Request) -> Optional[int]:
        """Round-robin routing among available targets."""
        available_targets = [
            i for i, target in enumerate(self.target_models)
            if target.can_accept_request()
        ]
        
        if not available_targets:
            return None
        
        # Simple round-robin (could be improved with state tracking)
        return available_targets[0]
    
    def get_status(self) -> dict:
        """Get current status of the router."""
        return {
            "queue_length": len(self.queue),
            "queue_utilization": len(self.queue) / self.queue_size,
            "total_routed": self.total_routed,
            "routing_algorithm": self.routing_algorithm
        }
