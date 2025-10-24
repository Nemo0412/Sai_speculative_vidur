"""
Configuration file for the scheduling algorithm system.
Modify these parameters to generate different scenarios.
"""

# System Configuration
K_DRAFT_MODELS = 20  # Number of draft models
N_TARGET_MODELS = 4  # Number of target models

# Router Configuration
ROUTER_QUEUE_SIZE = 50  # Router queue capacity (q_r)

# Target Model Configuration
# Each target model has its own queue size and batch size
TARGET_CONFIGS = [
    {"queue_size": 20, "batch_size": 5},  # Target 0
    {"queue_size": 15, "batch_size": 4},  # Target 1
    {"queue_size": 25, "batch_size": 6},  # Target 2
    {"queue_size": 18, "batch_size": 4},  # Target 3
]

# Request Processing Times (K*N matrix for each request type)
# Format: [draft_model][target_model] = processing_time
PREFILL_TIMES = [
    [2.0, 1.5, 2.5, 1.8],  # Draft 0 -> Target 0,1,2,3
    [1.8, 2.2, 1.9, 2.1],  # Draft 1 -> Target 0,1,2,3
    [2.3, 1.7, 2.0, 1.6],  # Draft 2 -> Target 0,1,2,3
    [1.9, 2.1, 1.8, 2.0],  # Draft 3 -> Target 0,1,2,3
    [2.2, 1.6, 2.3, 1.7],  # Draft 4 -> Target 0,1,2,3
    [1.7, 2.3, 1.6, 2.2],  # Draft 5 -> Target 0,1,2,3
    [2.1, 1.8, 2.1, 1.9],  # Draft 6 -> Target 0,1,2,3
    [1.6, 2.0, 1.7, 2.3],  # Draft 7 -> Target 0,1,2,3
    [2.4, 1.9, 2.2, 1.5],  # Draft 8 -> Target 0,1,2,3
    [1.8, 2.4, 1.9, 2.1],  # Draft 9 -> Target 0,1,2,3
    [2.0, 1.7, 2.4, 1.8],  # Draft 10 -> Target 0,1,2,3
    [1.9, 2.0, 1.5, 2.4],  # Draft 11 -> Target 0,1,2,3
    [2.3, 1.8, 2.0, 1.6],  # Draft 12 -> Target 0,1,2,3
    [1.7, 2.2, 1.8, 2.2],  # Draft 13 -> Target 0,1,2,3
    [2.1, 1.9, 2.3, 1.7],  # Draft 14 -> Target 0,1,2,3
    [1.8, 2.1, 1.6, 2.3],  # Draft 15 -> Target 0,1,2,3
    [2.2, 1.6, 2.1, 1.9],  # Draft 16 -> Target 0,1,2,3
    [1.6, 2.3, 1.9, 2.0],  # Draft 17 -> Target 0,1,2,3
    [2.0, 1.8, 2.2, 1.6],  # Draft 18 -> Target 0,1,2,3
    [1.9, 2.0, 1.7, 2.2],  # Draft 19 -> Target 0,1,2,3
]

DECODE_TIMES = [
    [1.0, 0.8, 1.2, 0.9],  # Draft 0 -> Target 0,1,2,3
    [0.9, 1.1, 0.95, 1.05], # Draft 1 -> Target 0,1,2,3
    [1.15, 0.85, 1.0, 0.8], # Draft 2 -> Target 0,1,2,3
    [0.95, 1.05, 0.9, 1.0], # Draft 3 -> Target 0,1,2,3
    [1.1, 0.8, 1.15, 0.85], # Draft 4 -> Target 0,1,2,3
    [0.85, 1.15, 0.8, 1.1], # Draft 5 -> Target 0,1,2,3
    [1.05, 0.9, 1.05, 0.95], # Draft 6 -> Target 0,1,2,3
    [0.8, 1.0, 0.85, 1.15], # Draft 7 -> Target 0,1,2,3
    [1.2, 0.95, 1.1, 0.75], # Draft 8 -> Target 0,1,2,3
    [0.9, 1.2, 0.95, 1.05], # Draft 9 -> Target 0,1,2,3
    [1.0, 0.85, 1.2, 0.9],  # Draft 10 -> Target 0,1,2,3
    [0.95, 1.0, 0.75, 1.2], # Draft 11 -> Target 0,1,2,3
    [1.15, 0.9, 1.0, 0.8],  # Draft 12 -> Target 0,1,2,3
    [0.85, 1.1, 0.9, 1.1],  # Draft 13 -> Target 0,1,2,3
    [1.05, 0.95, 1.15, 0.85], # Draft 14 -> Target 0,1,2,3
    [0.9, 1.05, 0.8, 1.15], # Draft 15 -> Target 0,1,2,3
    [1.1, 0.8, 1.05, 0.95], # Draft 16 -> Target 0,1,2,3
    [0.8, 1.15, 0.95, 1.0], # Draft 17 -> Target 0,1,2,3
    [1.0, 0.9, 1.1, 0.8],   # Draft 18 -> Target 0,1,2,3
    [0.95, 1.0, 0.85, 1.1], # Draft 19 -> Target 0,1,2,3
]

# Simulation Configuration
SIMULATION_TIME = 150.0  # Total simulation time
REQUEST_ARRIVAL_RATE = 1.0  # Requests per time unit

# Algorithm Configuration
ROUTING_ALGORITHM = "shortest_queue"  # Options: "shortest_queue", "least_loaded", "round_robin"
SCHEDULING_ALGORITHM = "shortest_job_first"  # Options: "shortest_job_first", "fifo", "priority"

# Validation
def validate_config():
    """Validate configuration parameters."""
    assert K_DRAFT_MODELS > 0, "K_DRAFT_MODELS must be positive"
    assert N_TARGET_MODELS > 0, "N_TARGET_MODELS must be positive"
    assert ROUTER_QUEUE_SIZE > 0, "ROUTER_QUEUE_SIZE must be positive"
    assert len(TARGET_CONFIGS) == N_TARGET_MODELS, "TARGET_CONFIGS length must match N_TARGET_MODELS"
    
    for i, config in enumerate(TARGET_CONFIGS):
        assert config["queue_size"] > 0, f"Target {i} queue_size must be positive"
        assert config["batch_size"] > 0, f"Target {i} batch_size must be positive"
        assert config["batch_size"] <= config["queue_size"], f"Target {i} batch_size must be <= queue_size"
    
    assert len(PREFILL_TIMES) == K_DRAFT_MODELS, "PREFILL_TIMES must have K_DRAFT_MODELS rows"
    assert len(DECODE_TIMES) == K_DRAFT_MODELS, "DECODE_TIMES must have K_DRAFT_MODELS rows"
    
    for i, row in enumerate(PREFILL_TIMES):
        assert len(row) == N_TARGET_MODELS, f"PREFILL_TIMES row {i} must have N_TARGET_MODELS columns"
        assert all(t > 0 for t in row), f"PREFILL_TIMES row {i} must have positive values"
    
    for i, row in enumerate(DECODE_TIMES):
        assert len(row) == N_TARGET_MODELS, f"DECODE_TIMES row {i} must have N_TARGET_MODELS columns"
        assert all(t > 0 for t in row), f"DECODE_TIMES row {i} must have positive values"

if __name__ == "__main__":
    validate_config()
    print("Configuration validation passed!")
