import numpy as np
from pymoo.core.sampling import Sampling


class PermutationSequenceSampling(Sampling):
    def _do(self, problem, n_samples, **kwargs):
        samples = []
        for i in range(n_samples):
            samples.append(np.random.permutation(problem.n_var))
        return np.array(samples)


class PermutationCombinedRouteSampling(Sampling):
    def _do(self, problem, n_samples, **kwargs):
        samples = []
        n_values = problem.algo_data['num_requests']
        n_markers = problem.algo_data['num_vehicles'] - 1
        generator = np.random.default_rng()
        for i in range(n_samples):
            sample = np.random.permutation(n_values)
            marker_ix = generator.choice(n_values, size=n_markers, replace=False)
            sample = np.insert(sample, marker_ix, np.full(n_markers, -1))
            samples.append(sample)
        return np.array(samples)
