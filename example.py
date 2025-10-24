"""
Example script demonstrating the scheduling algorithm system.
"""

from simulation import SchedulingSimulation
from optimization import SchedulingOptimizer
from config import validate_config
import json


def run_basic_example():
    """Run a basic simulation example."""
    print("=" * 60)
    print("BASIC SIMULATION EXAMPLE")
    print("=" * 60)
    
    # Validate configuration
    try:
        validate_config()
        print("✓ Configuration validation passed")
    except Exception as e:
        print(f"✗ Configuration validation failed: {e}")
        return
    
    # Run simulation
    simulation = SchedulingSimulation()
    result = simulation.run_simulation(simulation_time=50.0)
    
    # Print results
    simulation.print_results(result)
    
    # Save results
    simulation.save_results(result, "basic_example_results.json")
    
    return result


def run_optimization_example():
    """Run optimization example."""
    print("\n" + "=" * 60)
    print("OPTIMIZATION EXAMPLE")
    print("=" * 60)
    
    optimizer = SchedulingOptimizer()
    
    # Run exhaustive optimization
    print("Running exhaustive search optimization...")
    result = optimizer.optimize_exhaustive(simulation_time=30.0, metric="average_response_time")
    
    # Save results
    optimizer.save_optimization_results(result, "optimization_example.json")
    
    return result


def run_custom_configuration_example():
    """Run example with custom configuration."""
    print("\n" + "=" * 60)
    print("CUSTOM CONFIGURATION EXAMPLE")
    print("=" * 60)
    
    # Modify configuration
    import config as config_module
    
    # Save original values
    original_routing = config_module.ROUTING_ALGORITHM
    original_scheduling = config_module.SCHEDULING_ALGORITHM
    original_simulation_time = config_module.SIMULATION_TIME
    
    try:
        # Set custom configuration
        config_module.ROUTING_ALGORITHM = "least_loaded"
        config_module.SCHEDULING_ALGORITHM = "shortest_job_first"
        config_module.SIMULATION_TIME = 40.0
        
        print(f"Custom configuration:")
        print(f"  Routing: {config_module.ROUTING_ALGORITHM}")
        print(f"  Scheduling: {config_module.SCHEDULING_ALGORITHM}")
        print(f"  Simulation time: {config_module.SIMULATION_TIME}")
        
        # Run simulation
        simulation = SchedulingSimulation()
        result = simulation.run_simulation()
        
        # Print results
        simulation.print_results(result)
        
        # Save results
        simulation.save_results(result, "custom_config_results.json")
        
        return result
        
    finally:
        # Restore original configuration
        config_module.ROUTING_ALGORITHM = original_routing
        config_module.SCHEDULING_ALGORITHM = original_scheduling
        config_module.SIMULATION_TIME = original_simulation_time


def compare_algorithms():
    """Compare different algorithm combinations."""
    print("\n" + "=" * 60)
    print("ALGORITHM COMPARISON")
    print("=" * 60)
    
    routing_algorithms = ["shortest_queue", "least_loaded", "round_robin"]
    scheduling_algorithms = ["shortest_job_first", "fifo", "priority"]
    
    results = []
    
    for routing in routing_algorithms:
        for scheduling in scheduling_algorithms:
            print(f"\nTesting: {routing} + {scheduling}")
            
            # Set configuration
            import config as config_module
            original_routing = config_module.ROUTING_ALGORITHM
            original_scheduling = config_module.SCHEDULING_ALGORITHM
            
            try:
                config_module.ROUTING_ALGORITHM = routing
                config_module.SCHEDULING_ALGORITHM = scheduling
                
                # Run simulation
                simulation = SchedulingSimulation()
                result = simulation.run_simulation(simulation_time=25.0)
                
                results.append({
                    "routing": routing,
                    "scheduling": scheduling,
                    "average_response_time": result.average_response_time,
                    "throughput": result.throughput,
                    "completion_rate": result.completion_rate
                })
                
                print(f"  Response time: {result.average_response_time:.2f}")
                print(f"  Throughput: {result.throughput:.2f}")
                print(f"  Completion: {result.completion_rate:.2%}")
                
            finally:
                config_module.ROUTING_ALGORITHM = original_routing
                config_module.SCHEDULING_ALGORITHM = original_scheduling
    
    # Find best configurations
    best_response_time = min(results, key=lambda x: x["average_response_time"])
    best_throughput = max(results, key=lambda x: x["throughput"])
    best_completion = max(results, key=lambda x: x["completion_rate"])
    
    print("\n" + "=" * 40)
    print("BEST CONFIGURATIONS")
    print("=" * 40)
    print(f"Best response time: {best_response_time['routing']} + {best_response_time['scheduling']} ({best_response_time['average_response_time']:.2f})")
    print(f"Best throughput: {best_throughput['routing']} + {best_throughput['scheduling']} ({best_throughput['throughput']:.2f})")
    print(f"Best completion: {best_completion['routing']} + {best_completion['scheduling']} ({best_completion['completion_rate']:.2%})")
    
    # Save comparison results
    with open("algorithm_comparison.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nComparison results saved to algorithm_comparison.json")
    
    return results


def main():
    """Main function to run all examples."""
    print("Scheduling Algorithm System - Examples")
    print("=" * 50)
    
    try:
        # Run basic example
        basic_result = run_basic_example()
        
        # Run custom configuration example
        custom_result = run_custom_configuration_example()
        
        # Compare algorithms
        comparison_results = compare_algorithms()
        
        # Run optimization (optional, takes longer)
        run_optimization = input("\nRun optimization example? (y/n): ").lower().strip() == 'y'
        if run_optimization:
            optimization_result = run_optimization_example()
        
        print("\n" + "=" * 60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("Check the generated JSON files for detailed results:")
        print("  - basic_example_results.json")
        print("  - custom_config_results.json")
        print("  - algorithm_comparison.json")
        if run_optimization:
            print("  - optimization_example.json")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
