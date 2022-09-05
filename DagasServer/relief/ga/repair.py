import numpy as np
from pymoo.core.repair import Repair


class RepetitionRepair(Repair):
    def _do(self, problem, X, **kwargs):
        for i, chromosome in enumerate(X):
            unique_genes, count = np.unique(chromosome, return_counts=True)
            unique_mask = np.isin(chromosome, unique_genes[count > 1])  # locate all elements with duplicates
            new_values = np.setdiff1d(np.arange(len(chromosome)), chromosome[~unique_mask])
            np.random.shuffle(new_values)
            chromosome[unique_mask] = new_values
            X[i] = chromosome
        return X