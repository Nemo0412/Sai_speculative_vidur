"""
Main simulation system for the scheduling algorithm.
"""

import random
import time
from typing import List, Dict, Tuple
from dataclasses import dataclass
import json

from config import *
from models import Request, RequestType, TargetModel, Router


@dataclass
class SimulationResult:
    """Results from a simulation run."""
    total_requests: int
    completed_requests: int
    total_processing_time: float
    average_response_time: float
    throughput: float
    router_utilization: float
    target_utilizations: List[float]
    completion_rate: float


class SchedulingSimulation:
    """Main simulation class for the scheduling system."""
    
    def __init__(self):
        self.validate_config()
        self.setup_system()
        self.request_counter = 0
        self.completed_requests: List[Request] = []
        self.current_time = 0.0
        
    def validate_config(self):
        """Validate configuration before starting simulation."""
        validate_config()
        
    def setup_system(self):
        """Initialize the system components."""
        # Create target models
        self.target_models = []
        for i in range(N_TARGET_MODELS):
            config = TARGET_CONFIGS[i]
            target = TargetModel(i, config["queue_size"], config["batch_size"])
            self.target_models.append(target)
        
        # Create router
        self.router = Router(ROUTER_QUEUE_SIZE, self.target_models)
        self.router.routing_algorithm = ROUTING_ALGORITHM
        
        # Set scheduling algorithm for all targets
        for target in self.target_models:
            target.scheduling_algorithm = SCHEDULING_ALGORITHM
    
    def generate_request(self, current_time: float) -> Tuple[Request, Request]:
        """Generate a pair of prefill and decode requests for a random draft model."""
        draft_id = random.randint(0, K_DRAFT_MODELS - 1)
        
        # Generate prefill request
        prefill_request = Request(
            request_id=self.request_counter,
            draft_model_id=draft_id,
            request_type=RequestType.PREFILL,
            arrival_time=current_time
        )
        self.request_counter += 1
        
        # Generate corresponding decode request
        decode_request = Request(
            request_id=self.request_counter,
            draft_model_id=draft_id,
            request_type=RequestType.DECODE,
            arrival_time=current_time
        )
        self.request_counter += 1
        
        return prefill_request, decode_request
    
    def assign_processing_times(self, request: Request, target_id: int):
        """Assign processing time to a request based on its target."""
        if request.request_type == RequestType.PREFILL:
            request.processing_time = PREFILL_TIMES[request.draft_model_id][target_id]
        else:
            request.processing_time = DECODE_TIMES[request.draft_model_id][target_id]
    
    def ensure_same_target_for_draft(self, prefill_request: Request, decode_request: Request):
        """Ensure both requests from the same draft go to the same target."""
        if prefill_request.target_model_id is not None:
            decode_request.target_model_id = prefill_request.target_model_id
            self.assign_processing_times(decode_request, prefill_request.target_model_id)
        elif decode_request.target_model_id is not None:
            prefill_request.target_model_id = decode_request.target_model_id
            self.assign_processing_times(prefill_request, decode_request.target_model_id)
    
    def run_simulation(self, simulation_time: float = None) -> SimulationResult:
        """Run the simulation for the specified time."""
        if simulation_time is None:
            simulation_time = SIMULATION_TIME
        
        print(f"Starting simulation for {simulation_time} time units...")
        print(f"Configuration: {K_DRAFT_MODELS} draft models, {N_TARGET_MODELS} target models")
        print(f"Router queue size: {ROUTER_QUEUE_SIZE}")
        print(f"Routing algorithm: {ROUTING_ALGORITHM}")
        print(f"Scheduling algorithm: {SCHEDULING_ALGORITHM}")
        print("-" * 50)
        
        # Generate initial requests
        initial_requests = []
        for _ in range(int(REQUEST_ARRIVAL_RATE * simulation_time)):
            prefill_req, decode_req = self.generate_request(0.0)
            initial_requests.extend([prefill_req, decode_req])
        
        # Add requests to router queue
        for request in initial_requests:
            if self.router.can_accept_request():
                self.router.add_request(request)
        
        # Main simulation loop
        time_step = 0.1
        self.current_time = 0.0
        
        while self.current_time < simulation_time:
            # Generate new requests based on arrival rate
            if random.random() < REQUEST_ARRIVAL_RATE * time_step:
                prefill_req, decode_req = self.generate_request(self.current_time)
                
                # Try to add to router queue
                if self.router.can_accept_request():
                    self.router.add_request(prefill_req)
                    self.router.add_request(decode_req)
            
            # Route requests from router to targets
            routed_count = self.router.route_requests(self.current_time)
            
            # Process batches on all targets
            for target in self.target_models:
                # Start new batch if possible
                if target.can_start_new_batch():
                    target.start_new_batch(self.current_time, SCHEDULING_ALGORITHM)
                
                # Process current batch
                completed = target.process_batch(self.current_time)
                self.completed_requests.extend(completed)
            
            # Ensure draft requests go to same target
            self._ensure_draft_consistency()
            
            self.current_time += time_step
        
        # Process remaining requests
        self._finish_remaining_requests()
        
        return self._calculate_results()
    
    def _ensure_draft_consistency(self):
        """Ensure requests from the same draft go to the same target."""
        # Group requests by draft model
        draft_requests = {}
        for request in self.router.queue:
            if request.draft_model_id not in draft_requests:
                draft_requests[request.draft_model_id] = []
            draft_requests[request.draft_model_id].append(request)
        
        # Check consistency and fix if needed
        for draft_id, requests in draft_requests.items():
            if len(requests) >= 2:  # Both prefill and decode
                prefill_req = next((r for r in requests if r.request_type == RequestType.PREFILL), None)
                decode_req = next((r for r in requests if r.request_type == RequestType.DECODE), None)
                
                if prefill_req and decode_req:
                    self.ensure_same_target_for_draft(prefill_req, decode_req)
    
    def _finish_remaining_requests(self):
        """Process all remaining requests to completion."""
        print("Finishing remaining requests...")
        
        # Continue processing until all queues are empty
        max_iterations = 1000
        iteration = 0
        
        while (len(self.router.queue) > 0 or 
               any(len(target.queue) > 0 or target.is_batch_ready() for target in self.target_models)):
            
            if iteration >= max_iterations:
                print("Warning: Maximum iterations reached, stopping simulation")
                break
            
            # Route remaining requests
            self.router.route_requests(self.current_time)
            
            # Process all targets
            for target in self.target_models:
                if target.can_start_new_batch():
                    target.start_new_batch(self.current_time, SCHEDULING_ALGORITHM)
                
                completed = target.process_batch(self.current_time)
                self.completed_requests.extend(completed)
            
            self.current_time += 0.1
            iteration += 1
    
    def _calculate_results(self) -> SimulationResult:
        """Calculate simulation results."""
        total_requests = self.request_counter
        completed_requests = len(self.completed_requests)
        
        if completed_requests == 0:
            return SimulationResult(
                total_requests=total_requests,
                completed_requests=0,
                total_processing_time=0.0,
                average_response_time=0.0,
                throughput=0.0,
                router_utilization=0.0,
                target_utilizations=[0.0] * N_TARGET_MODELS,
                completion_rate=0.0
            )
        
        # Calculate metrics
        total_processing_time = sum(req.processing_time for req in self.completed_requests)
        response_times = [req.end_time - req.arrival_time for req in self.completed_requests if req.end_time]
        average_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        
        throughput = completed_requests / self.current_time if self.current_time > 0 else 0.0
        router_utilization = len(self.router.queue) / self.router.queue_size
        
        target_utilizations = [target.get_queue_utilization() for target in self.target_models]
        completion_rate = completed_requests / total_requests if total_requests > 0 else 0.0
        
        return SimulationResult(
            total_requests=total_requests,
            completed_requests=completed_requests,
            total_processing_time=total_processing_time,
            average_response_time=average_response_time,
            throughput=throughput,
            router_utilization=router_utilization,
            target_utilizations=target_utilizations,
            completion_rate=completion_rate
        )
    
    def print_results(self, result: SimulationResult):
        """Print simulation results in a formatted way."""
        print("\n" + "="*60)
        print("SIMULATION RESULTS")
        print("="*60)
        print(f"Total requests generated: {result.total_requests}")
        print(f"Completed requests: {result.completed_requests}")
        print(f"Completion rate: {result.completion_rate:.2%}")
        print(f"Total processing time: {result.total_processing_time:.2f}")
        print(f"Average response time: {result.average_response_time:.2f}")
        print(f"Throughput: {result.throughput:.2f} requests/time unit")
        print(f"Router utilization: {result.router_utilization:.2%}")
        print("\nTarget Model Utilizations:")
        for i, utilization in enumerate(result.target_utilizations):
            print(f"  Target {i}: {utilization:.2%}")
        print("="*60)
    
    def save_results(self, result: SimulationResult, filename: str = "simulation_results.json"):
        """Save simulation results to a JSON file."""
        data = {
            "configuration": {
                "k_draft_models": K_DRAFT_MODELS,
                "n_target_models": N_TARGET_MODELS,
                "router_queue_size": ROUTER_QUEUE_SIZE,
                "routing_algorithm": ROUTING_ALGORITHM,
                "scheduling_algorithm": SCHEDULING_ALGORITHM,
                "simulation_time": SIMULATION_TIME
            },
            "results": {
                "total_requests": result.total_requests,
                "completed_requests": result.completed_requests,
                "completion_rate": result.completion_rate,
                "total_processing_time": result.total_processing_time,
                "average_response_time": result.average_response_time,
                "throughput": result.throughput,
                "router_utilization": result.router_utilization,
                "target_utilizations": result.target_utilizations
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Results saved to {filename}")


def main():
    """Main function to run the simulation."""
    # Validate configuration
    try:
        validate_config()
        print("Configuration validation passed!")
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return
    
    # Run simulation
    simulation = SchedulingSimulation()
    result = simulation.run_simulation()
    
    # Print and save results
    simulation.print_results(result)
    simulation.save_results(result)


if __name__ == "__main__":
    main()
