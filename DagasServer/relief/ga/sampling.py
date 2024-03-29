import random

import numpy as np
from pymoo.core.sampling import Sampling


class PermutationSequenceSampling(Sampling):
    def _do(self, problem, n_samples, **kwargs):
        samples = []
        for i in range(n_samples):
            samples.append(np.random.permutation(problem.n_var))
        return np.array(samples)


class ClosestDenseDepotSampling(Sampling):
    def _do(self, problem, n_samples, **kwargs):
        samples = []
        request_count = problem.algo_data['num_requests']
        distance_matrix_d2r = problem.algo_data['distance_matrix'][request_count:, :request_count]
        donor_count = problem.algo_data['num_vehicles']
        assignments = [None] * problem.n_var
        for request_ix in range(request_count):
            donors_sorted = np.argsort(distance_matrix_d2r[:, request_ix])
            for ix, donor_ix in enumerate(donors_sorted):
                gene = request_count * donor_ix + request_ix
                assignments[request_count * ix + request_ix] = gene
        for i in range(n_samples):
            samples.append(assignments)
        # itr_specimen = np.array(assignments)
        # samples.append(np.array(assignments))
        # for i in range(n_samples - 1):
        #     # ITR (Iterated Swap Procedure)
        #     swap_genes = random.sample(range(0, request_count * donor_count), 2)  # return 2 random genes
        #     itr_specimen[swap_genes[0]], itr_specimen[swap_genes[1]] = itr_specimen[swap_genes[1]], \
        #                                                                itr_specimen[swap_genes[0]]
        #     for swap_gene in swap_genes:
        #         sequence = itr_specimen[swap_gene-1:swap_gene+2]
        #         np.random.shuffle(sequence)
        #         itr_specimen[swap_gene-1:swap_gene+2] = sequence
        #     samples.append(itr_specimen)
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


class ClosestSoloDepotSampling(Sampling):
    def _do(self, problem, n_samples, **kwargs):
        samples = []
        request_count = problem.algo_data['num_requests']
        distance_matrix_d2r = problem.algo_data['distance_matrix']
        current_node = problem.algo_data['starts'][0]  # Donor
        visited_nodes = [current_node]
        route = []
        while not len(route) == request_count:
            requests_sorted = np.argsort(distance_matrix_d2r[:request_count, current_node])
            for request_ix in requests_sorted:
                if request_ix not in visited_nodes and not request_ix == current_node:
                    route.append(request_ix)
                    visited_nodes.append(request_ix)
                    current_node = request_ix
                    break
        # for i in range(n_samples):
        samples.append(np.array(route))
        itr_specimen = np.array(route)
        for i in range(n_samples - 1):
            # ITR (Iterated Swap Procedure)
            swap_genes = random.sample(range(1, request_count - 1), 2)  # return 2 random genes
            itr_specimen[swap_genes[0]], itr_specimen[swap_genes[1]] = itr_specimen[swap_genes[1]], \
                                                                       itr_specimen[swap_genes[0]]
            for swap_gene in swap_genes:
                sequence = itr_specimen[swap_gene - 1:swap_gene + 2]
                np.random.shuffle(sequence)
                itr_specimen[swap_gene - 1:swap_gene + 2] = sequence
            samples.append(itr_specimen)
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
