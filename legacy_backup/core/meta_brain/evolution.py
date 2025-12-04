import logging
import random
import numpy as np
from typing import List, Dict, Any

logger = logging.getLogger("EvolutionEngine")

class Agent:
    def __init__(self, agent_id: int, hyperparameters: Dict[str, float]):
        self.id = agent_id
        self.hyperparameters = hyperparameters
        self.fitness = 0.0

    def __repr__(self):
        return f"Agent(id={self.id}, fitness={self.fitness:.4f}, params={self.hyperparameters})"

class EvolutionEngine:
    """
    Neuroevolution & Genetic Algorithms (Hyperparameter Tuning).
    Manages a population of agents, evolving them over generations to optimize hyperparameters.
    """
    def __init__(self, population_size: int = 10, mutation_rate: float = 0.1):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.generation = 0
        self.population: List[Agent] = []
        self.param_ranges = {
            "learning_rate": (0.0001, 0.01),
            "gamma": (0.90, 0.99),
            "batch_size": (32, 256),
            "ent_coef": (0.0, 0.1)
        }
        self._initialize_population()

    def _initialize_population(self):
        logger.info(f"Initializing population of {self.population_size} agents...")
        for i in range(self.population_size):
            params = {
                k: random.uniform(v[0], v[1]) if k != "batch_size" else int(random.uniform(v[0], v[1]))
                for k, v in self.param_ranges.items()
            }
            self.population.append(Agent(i, params))

    def evaluate_fitness(self, agent: Agent, market_data: Any) -> float:
        """
        Simulate agent performance to calculate fitness.
        In a real scenario, this would run a backtest or live trade session.
        """
        # Mock fitness calculation based on random market performance + param "goodness"
        # Favor lower learning rate and higher gamma for this mock
        score = (1.0 / agent.hyperparameters["learning_rate"]) * 0.0001 + \
                (agent.hyperparameters["gamma"] * 10) + \
                random.uniform(-5, 5)
        return max(0.0, score)

    def evolve(self):
        """
        Run one generation of evolution: Selection, Crossover, Mutation.
        """
        self.generation += 1
        logger.info(f"--- Starting Generation {self.generation} ---")

        # 1. Evaluate Fitness
        for agent in self.population:
            agent.fitness = self.evaluate_fitness(agent, None)
        
        # Sort by fitness (descending)
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        best_agent = self.population[0]
        logger.info(f"Best Agent: {best_agent}")

        # 2. Selection (Keep top 20% as elites)
        elite_count = int(self.population_size * 0.2)
        new_population = self.population[:elite_count]

        # 3. Crossover & Mutation to fill the rest
        while len(new_population) < self.population_size:
            parent1 = random.choice(self.population[:elite_count])
            parent2 = random.choice(self.population[:elite_count])
            child = self._crossover(parent1, parent2)
            self._mutate(child)
            new_population.append(child)

        self.population = new_population
        logger.info("Generation complete.")

    def _crossover(self, parent1: Agent, parent2: Agent) -> Agent:
        """
        Mix genes (hyperparameters) from two parents.
        """
        child_params = {}
        for key in self.param_ranges:
            if random.random() > 0.5:
                child_params[key] = parent1.hyperparameters[key]
            else:
                child_params[key] = parent2.hyperparameters[key]
        
        # Create new agent ID
        new_id = int(f"{self.generation}{random.randint(100,999)}")
        return Agent(new_id, child_params)

    def _mutate(self, agent: Agent):
        """
        Randomly alter genes based on mutation rate.
        """
        for key, (min_val, max_val) in self.param_ranges.items():
            if random.random() < self.mutation_rate:
                if isinstance(min_val, int):
                    agent.hyperparameters[key] = int(random.uniform(min_val, max_val))
                else:
                    agent.hyperparameters[key] = random.uniform(min_val, max_val)
