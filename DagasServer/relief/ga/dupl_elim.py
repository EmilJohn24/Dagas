import numpy as np
from pymoo.core.duplicate import ElementwiseDuplicateElimination


class SimpleDuplicationElimination(ElementwiseDuplicateElimination):
    def is_equal(self, a, b):
        return np.array_equal(a.X, b.X)