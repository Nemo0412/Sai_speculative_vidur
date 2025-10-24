"""
Optimization algorithms for finding the best scheduling strategies.
"""

import itertools
import time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import json

from simulation import SchedulingSimulation, SimulationResult


@dataclass
class OptimizationResult:
    """Results from optimization process."""
    best_configuration: Dict
    best_result: SimulationResult
    all_results: List[Tuple[Dict, SimulationResult]]
    optimization_time: float


class SchedulingOptimizer:
    """Optimizer for finding the best scheduling configuration."""
    
    def __init__(self):
        self.routing_algorithms = ["shortest_queue", "least_loaded", "round_robin"]
        self.scheduling_algorithms = ["shortest_job_first", "fifo", "priority"]
        self.optimization_metrics = ["average_response_time", "throughput", "completion_rate"]
    
    def optimize_exhaustive(self, simulation_time: float = 50.0, 
                          metric: str = "average_response_time") -> OptimizationResult:
        """
        Exhaustive search over all algorithm combinations.
        
        Args:
            simulation_time: Time to run each simulation
            metric: Metric to optimize (lower is better for response time, higher for others)
        """
        print(f"Starting exhaustive optimization for {simulation_time} time units...")
        print(f"Optimizing metric: {metric}")
        print(f"Testing {len(self.routing_algorithms)} routing × {len(self.scheduling_algorithms)} scheduling = {len(self.routing_algorithms) * len(self.scheduling_algorithms)} combinations")
        print("-" * 60)
        
        start_time = time.time()
        all_results = []
        
        for routing_alg in self.routing_algorithms:
            for scheduling_alg in self.scheduling_algorithms:
                print(f"Testing: {routing_alg} + {scheduling_alg}")
                
                # Create configuration
                config = {
                    "routing_algorithm": routing_alg,
                    "scheduling_algorithm": scheduling_alg
                }
                
                # Run simulation with this configuration
                result = self._run_simulation_with_config(config, simulation_time)
                all_results.append((config, result))
                
                # Print result
                metric_value = getattr(result, metric)
                print(f"  {metric}: {metric_value:.4f}, completion: {result.completion_rate:.2%}")
        
        # Find best configuration
        if metric == "average_response_time":
            best_config, best_result = min(all_results, key=lambda x: getattr(x[1], metric))
        else:
            best_config, best_result = max(all_results, key=lambda x: getattr(x[1], metric))
        
        optimization_time = time.time() - start_time
        
        print("\n" + "="*60)
        print("OPTIMIZATION RESULTS")
        print("="*60)
        print(f"Best configuration: {best_config}")
        print(f"Best {metric}: {getattr(best_result, metric):.4f}")
        print(f"Optimization time: {optimization_time:.2f} seconds")
        print("="*60)
        
        return OptimizationResult(
            best_configuration=best_config,
            best_result=best_result,
            all_results=all_results,
            optimization_time=optimization_time
        )
    
    def optimize_genetic_algorithm(self, simulation_time: float = 30.0, 
                                 population_size: int = 10, generations: int = 5,
                                 metric: str = "average_response_time") -> OptimizationResult:
        """
        Genetic algorithm optimization for scheduling strategies.
        
        Args:
            simulation_time: Time to run each simulation
            population_size: Size of each generation
            generations: Number of generations to evolve
            metric: Metric to optimize
        """
        print(f"Starting genetic algorithm optimization...")
        print(f"Population size: {population_size}, Generations: {generations}")
        print(f"Simulation time per individual: {simulation_time}")
        print("-" * 60)
        
        start_time = time.time()
        
        # Initialize population
        population = self._initialize_population(population_size)
        all_results = []
        
        for generation in range(generations):
            print(f"\nGeneration {generation + 1}/{generations}")
            
            # Evaluate population
            generation_results = []
            for i, individual in enumerate(population):
                print(f"  Evaluating individual {i+1}/{len(population)}: {individual}")
                result = self._run_simulation_with_config(individual, simulation_time)
                generation_results.append((individual, result))
                all_results.append((individual, result))
            
            # Sort by fitness
            if metric == "average_response_time":
                generation_results.sort(key=lambda x: getattr(x[1], metric))
            else:
                generation_results.sort(key=lambda x: getattr(x[1], metric), reverse=True)
            
            # Select best individuals for next generation
            elite_size = population_size // 2
            elite = [individual for individual, _ in generation_results[:elite_size]]
            
            # Generate new population through crossover and mutation
            new_population = elite.copy()
            while len(new_population) < population_size:
                parent1, parent2 = self._select_parents(generation_results)
                child = self._crossover(parent1, parent2)
                child = self._mutate(child)
                new_population.append(child)
            
            population = new_population
            
            # Print best result of this generation
            best_individual, best_result = generation_results[0]
            best_metric = getattr(best_result, metric)
            print(f"  Best {metric}: {best_metric:.4f} ({best_individual})")
        
        # Find overall best
        if metric == "average_response_time":
            best_config, best_result = min(all_results, key=lambda x: getattr(x[1], metric))
        else:
            best_config, best_result = max(all_results, key=lambda x: getattr(x[1], metric))
        
        optimization_time = time.time() - start_time
        
        print("\n" + "="*60)
        print("GENETIC ALGORITHM RESULTS")
        print("="*60)
        print(f"Best configuration: {best_config}")
        print(f"Best {metric}: {getattr(best_result, metric):.4f}")
        print(f"Optimization time: {optimization_time:.2f} seconds")
        print("="*60)
        
        return OptimizationResult(
            best_configuration=best_config,
            best_result=best_result,
            all_results=all_results,
            optimization_time=optimization_time
        )
    
    def _initialize_population(self, size: int) -> List[Dict]:
        """Initialize random population of configurations."""
        import random
        population = []
        
        for _ in range(size):
            config = {
                "routing_algorithm": random.choice(self.routing_algorithms),
                "scheduling_algorithm": random.choice(self.scheduling_algorithms)
            }
            population.append(config)
        
        return population
    
    def _select_parents(self, results: List[Tuple[Dict, SimulationResult]]) -> Tuple[Dict, Dict]:
        """Select two parents using tournament selection."""
        import random
        
        # Tournament selection
        tournament_size = 3
        parent1 = self._tournament_selection(results, tournament_size)
        parent2 = self._tournament_selection(results, tournament_size)
        
        return parent1, parent2
    
    def _tournament_selection(self, results: List[Tuple[Dict, SimulationResult]], 
                            tournament_size: int) -> Dict:
        """Tournament selection for parent selection."""
        import random
        
        tournament = random.sample(results, min(tournament_size, len(results)))
        # Return the best individual from the tournament
        return min(tournament, key=lambda x: x[1].average_response_time)[0]
    
    def _crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        """Create offspring through crossover."""
        import random
        
        child = {}
        for key in parent1:
            if random.random() < 0.5:
                child[key] = parent1[key]
            else:
                child[key] = parent2[key]
        
        return child
    
    def _mutate(self, individual: Dict) -> Dict:
        """Mutate an individual."""
        import random
        
        mutated = individual.copy()
        
        if random.random() < 0.3:  # 30% mutation rate
            mutated["routing_algorithm"] = random.choice(self.routing_algorithms)
        
        if random.random() < 0.3:  # 30% mutation rate
            mutated["scheduling_algorithm"] = random.choice(self.scheduling_algorithms)
        
        return mutated
    
    def _run_simulation_with_config(self, config: Dict, simulation_time: float) -> SimulationResult:
        """Run simulation with specific configuration."""
        # Temporarily modify global configuration
        import config as config_module
        
        original_routing = config_module.ROUTING_ALGORITHM
        original_scheduling = config_module.SCHEDULING_ALGORITHM
        
        try:
            config_module.ROUTING_ALGORITHM = config["routing_algorithm"]
            config_module.SCHEDULING_ALGORITHM = config["scheduling_algorithm"]
            
            simulation = SchedulingSimulation()
            result = simulation.run_simulation(simulation_time)
            
            return result
        finally:
            # Restore original configuration
            config_module.ROUTING_ALGORITHM = original_routing
            config_module.SCHEDULING_ALGORITHM = original_scheduling
    
    def save_optimization_results(self, result: OptimizationResult, filename: str = "optimization_results.json"):
        """Save optimization results to JSON file."""
        data = {
            "optimization_type": "exhaustive",
            "best_configuration": result.best_configuration,
            "best_metrics": {
                "total_requests": result.best_result.total_requests,
                "completed_requests": result.best_result.completed_requests,
                "completion_rate": result.best_result.completion_rate,
                "average_response_time": result.best_result.average_response_time,
                "throughput": result.best_result.throughput,
                "router_utilization": result.best_result.router_utilization,
                "target_utilizations": result.best_result.target_utilizations
            },
            "all_results": [
                {
                    "configuration": config,
                    "metrics": {
                        "total_requests": sim_result.total_requests,
                        "completed_requests": sim_result.completed_requests,
                        "completion_rate": sim_result.completion_rate,
                        "average_response_time": sim_result.average_response_time,
                        "throughput": sim_result.throughput,
                        "router_utilization": sim_result.router_utilization,
                        "target_utilizations": sim_result.target_utilizations
                    }
                }
                for config, sim_result in result.all_results
            ],
            "optimization_time": result.optimization_time
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Optimization results saved to {filename}")


def main():
    """Main function for optimization."""
    optimizer = SchedulingOptimizer()
    
    print("Scheduling Algorithm Optimization")
    print("=" * 40)
    print("1. Exhaustive Search")
    print("2. Genetic Algorithm")
    print("3. Both")
    
    choice = input("Select optimization method (1-3): ").strip()
    
    if choice == "1":
        result = optimizer.optimize_exhaustive(simulation_time=30.0)
        optimizer.save_optimization_results(result, "exhaustive_optimization.json")
    elif choice == "2":
        result = optimizer.optimize_genetic_algorithm(simulation_time=20.0, generations=3)
        optimizer.save_optimization_results(result, "genetic_optimization.json")
    elif choice == "3":
        print("\nRunning exhaustive search...")
        exhaustive_result = optimizer.optimize_exhaustive(simulation_time=30.0)
        optimizer.save_optimization_results(exhaustive_result, "exhaustive_optimization.json")
        
        print("\nRunning genetic algorithm...")
        genetic_result = optimizer.optimize_genetic_algorithm(simulation_time=20.0, generations=3)
        optimizer.save_optimization_results(genetic_result, "genetic_optimization.json")
    else:
        print("Invalid choice. Running exhaustive search by default.")
        result = optimizer.optimize_exhaustive(simulation_time=30.0)
        optimizer.save_optimization_results(result)


if __name__ == "__main__":
    main()
