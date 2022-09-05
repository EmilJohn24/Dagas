import numpy as np
from pymoo.core.crossover import Crossover
from pymoo.operators.crossover.erx import EdgeRecombinationCrossover
from pymoo.operators.crossover.ox import OrderCrossover


# class CustomCrossover(Crossover):
#     def __init__(self, **kwargs):
#         super().__init__(2, 2, **kwargs)
#
#     def _do(self, problem, X, **kwargs):
#         recombined_X = []
#
#         for p1, p2 in zip(X[0], X[1]):
#             p1 = p1[p1 != -1]
#             p2 = p2[p2 != -1]
#             recombined_X.append([p1, p2])
#         recombined_X_np = np.array(recombined_X)
#         return OrderCrossover()._do(problem, recombined_X_np)