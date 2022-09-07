import numpy as np
from pymoo.core.sampling import Sampling


class PermutationSequenceSampling(Sampling):
    def _do(self, problem, n_samples, **kwargs):
        samples = []
        for i in range(n_samples):
            samples.append(np.random.permutation(problem.n_var))
        return np.array(samples)


class ClosestDepotSampling(Sampling):
    def _do(self, problem, n_samples, **kwargs):
        samples = []
        request_count = problem.algo_data['num_requests']
        donor_count = problem.algo_data['num_vehicles']
        # donor_ix, request_ix
        distance_matrix_d2r = problem.algo_data['distance_matrix'][request_count:, :request_count]
        donor_assignments = []
        for donor_ix in range(donor_count):
            donor_assignments.append([])
        for request_ix in range(request_count):
            closest_donor_ix = np.argmin(distance_matrix_d2r[:, request_ix])
            donor_assignments[closest_donor_ix].append(request_ix)
        for assignment_ix, donor_ix in enumerate(range(donor_count - 1)):
            donor_assignments[donor_ix].append(assignment_ix + request_count)
        for i in range(n_samples):
            samples.append(np.concatenate(donor_assignments).astype(int))
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
