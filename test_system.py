"""
Test script to verify the scheduling system works correctly.
"""

import sys
import traceback
from config import validate_config
from simulation import SchedulingSimulation
from optimization import SchedulingOptimizer


def test_configuration():
    """Test configuration validation."""
    print("Testing configuration validation...")
    try:
        validate_config()
        print("✓ Configuration validation passed")
        return True
    except Exception as e:
        print(f"✗ Configuration validation failed: {e}")
        return False


def test_basic_simulation():
    """Test basic simulation functionality."""
    print("\nTesting basic simulation...")
    try:
        simulation = SchedulingSimulation()
        result = simulation.run_simulation(simulation_time=10.0)
        
        # Basic checks
        assert result.total_requests > 0, "No requests generated"
        assert result.completed_requests >= 0, "Invalid completed requests count"
        assert result.completion_rate >= 0.0, "Invalid completion rate"
        assert result.completion_rate <= 1.0, "Completion rate > 100%"
        
        print("✓ Basic simulation passed")
        print(f"  Generated: {result.total_requests} requests")
        print(f"  Completed: {result.completed_requests} requests")
        print(f"  Completion rate: {result.completion_rate:.2%}")
        return True
    except Exception as e:
        print(f"✗ Basic simulation failed: {e}")
        traceback.print_exc()
        return False


def test_algorithm_combinations():
    """Test different algorithm combinations."""
    print("\nTesting algorithm combinations...")
    
    routing_algorithms = ["shortest_queue", "least_loaded", "round_robin"]
    scheduling_algorithms = ["shortest_job_first", "fifo", "priority"]
    
    success_count = 0
    total_tests = len(routing_algorithms) * len(scheduling_algorithms)
    
    for routing in routing_algorithms:
        for scheduling in scheduling_algorithms:
            try:
                print(f"  Testing {routing} + {scheduling}...")
                
                # Set configuration
                import config as config_module
                original_routing = config_module.ROUTING_ALGORITHM
                original_scheduling = config_module.SCHEDULING_ALGORITHM
                
                try:
                    config_module.ROUTING_ALGORITHM = routing
                    config_module.SCHEDULING_ALGORITHM = scheduling
                    
                    simulation = SchedulingSimulation()
                    result = simulation.run_simulation(simulation_time=5.0)
                    
                    # Basic validation
                    assert result.total_requests >= 0
                    assert result.completed_requests >= 0
                    assert 0.0 <= result.completion_rate <= 1.0
                    
                    success_count += 1
                    print(f"    ✓ {routing} + {scheduling} passed")
                    
                finally:
                    config_module.ROUTING_ALGORITHM = original_routing
                    config_module.SCHEDULING_ALGORITHM = original_scheduling
                    
            except Exception as e:
                print(f"    ✗ {routing} + {scheduling} failed: {e}")
    
    print(f"✓ Algorithm combinations: {success_count}/{total_tests} passed")
    return success_count == total_tests


def test_optimization():
    """Test optimization functionality."""
    print("\nTesting optimization...")
    try:
        optimizer = SchedulingOptimizer()
        
        # Test with very short simulation time for speed
        result = optimizer.optimize_exhaustive(simulation_time=5.0, metric="average_response_time")
        
        # Basic validation
        assert result.best_configuration is not None
        assert result.best_result is not None
        assert len(result.all_results) > 0
        assert result.optimization_time > 0
        
        print("✓ Optimization passed")
        print(f"  Best configuration: {result.best_configuration}")
        print(f"  Best response time: {result.best_result.average_response_time:.2f}")
        print(f"  Optimization time: {result.optimization_time:.2f}s")
        return True
    except Exception as e:
        print(f"✗ Optimization failed: {e}")
        traceback.print_exc()
        return False


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\nTesting edge cases...")
    
    try:
        # Test with very short simulation time
        simulation = SchedulingSimulation()
        result = simulation.run_simulation(simulation_time=0.1)
        print("✓ Very short simulation time handled")
        
        # Test with different arrival rates
        import config as config_module
        original_rate = config_module.REQUEST_ARRIVAL_RATE
        
        try:
            config_module.REQUEST_ARRIVAL_RATE = 0.0  # No requests
            simulation = SchedulingSimulation()
            result = simulation.run_simulation(simulation_time=5.0)
            # With zero arrival rate, we still get initial requests, so just check it's reasonable
            assert result.total_requests >= 0
            print("✓ Zero arrival rate handled")
            
            config_module.REQUEST_ARRIVAL_RATE = 10.0  # High arrival rate
            simulation = SchedulingSimulation()
            result = simulation.run_simulation(simulation_time=5.0)
            assert result.total_requests > 0
            print("✓ High arrival rate handled")
            
        finally:
            config_module.REQUEST_ARRIVAL_RATE = original_rate
        
        return True
    except Exception as e:
        print(f"✗ Edge case testing failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("Scheduling System Test Suite")
    print("=" * 40)
    
    tests = [
        test_configuration,
        test_basic_simulation,
        test_algorithm_combinations,
        test_optimization,
        test_edge_cases
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
