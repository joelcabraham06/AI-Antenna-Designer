"""
AI-Based Automatic Antenna Designer
Module: Multi-Objective Genetic Algorithm & Optimization Engine
"""

import numpy as np
from .surrogate import RFSurrogateModel
from .synthesis import AntennaSynthesizer

class AntennaOptimizer:
    def __init__(self, surrogate_model=None):
        self.surrogate = surrogate_model if surrogate_model else RFSurrogateModel()

    def evaluate_fitness(self, L, W, x_f, target_f0, target_s11=-10.0, target_gain=3.5, er=4.4, h=1.6):
        """
        Multi-Objective Fitness Function combining frequency matching, return loss S11, and gain.
        Lower Fitness Score = Superior Antenna Design.
        """
        pred = self.surrogate.predict(L, W, x_f, er, h)

        # 1. Frequency Matching Penalty
        freq_error = abs(pred["predicted_f_res_ghz"] - target_f0) * 50.0

        # 2. S11 Return Loss Penalty (Penalize if S11 > target_s11)
        s11_penalty = max(0.0, pred["predicted_s11_db"] - target_s11) * 2.0

        # 3. Gain Penalty (Penalize if Gain < target_gain)
        gain_penalty = max(0.0, target_gain - pred["predicted_gain_dbi"]) * 5.0

        fitness_score = freq_error + s11_penalty + gain_penalty
        return fitness_score, pred

    def optimize(self, target_f0_ghz, target_s11=-10.0, target_gain=3.5, er=4.4, h=1.6, generations=30, pop_size=20):
        """
        Executes Multi-Objective Genetic Algorithm to synthesize optimal antenna dimensions.
        """
        # Baseline seed from analytical transmission line formula
        init_geom = AntennaSynthesizer.calculate_microstrip_patch(target_f0_ghz, er, h)
        base_L = init_geom["patch_length_mm"]
        base_W = init_geom["patch_width_mm"]
        base_xf = init_geom["feed_offset_mm"]

        # Initialize Population around analytical seed
        population = []
        for _ in range(pop_size):
            L = base_L + np.random.uniform(-1.5, 1.5)
            W = base_W + np.random.uniform(-2.0, 2.0)
            xf = max(0.1, base_xf + np.random.uniform(-0.5, 0.5))
            population.append([L, W, xf])

        best_solution = None
        best_fitness = float('inf')
        best_pred = None
        history = []

        for gen in range(generations):
            scores = []
            for indiv in population:
                fit, pred = self.evaluate_fitness(indiv[0], indiv[1], indiv[2], target_f0_ghz, target_s11, target_gain, er, h)
                scores.append((fit, indiv, pred))

            scores.sort(key=lambda x: x[0])
            if scores[0][0] < best_fitness:
                best_fitness = scores[0][0]
                best_solution = scores[0][1]
                best_pred = scores[0][2]

            history.append({
                "generation": gen + 1,
                "best_fitness": round(best_fitness, 4),
                "best_s11": best_pred["predicted_s11_db"],
                "best_f_res": best_pred["predicted_f_res_ghz"]
            })

            # Genetic Selection, Crossover & Mutation
            survivors = [s[1] for s in scores[:pop_size // 2]]
            new_pop = list(survivors)

            while len(new_pop) < pop_size:
                p1, p2 = survivors[np.random.randint(0, len(survivors))], survivors[np.random.randint(0, len(survivors))]
                # Crossover
                child = [
                    (p1[0] + p2[0]) / 2.0 + np.random.normal(0, 0.1),
                    (p1[1] + p2[1]) / 2.0 + np.random.normal(0, 0.1),
                    max(0.1, (p1[2] + p2[2]) / 2.0 + np.random.normal(0, 0.05))
                ]
                new_pop.append(child)

            population = new_pop

        return {
            "target_f0_ghz": target_f0_ghz,
            "optimized_patch_length_mm": round(best_solution[0], 3),
            "optimized_patch_width_mm": round(best_solution[1], 3),
            "optimized_feed_offset_mm": round(best_solution[2], 3),
            "performance": best_pred,
            "best_fitness_score": round(best_fitness, 4),
            "optimization_history": history
        }
