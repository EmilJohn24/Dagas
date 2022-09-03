import copy
import sys
from itertools import islice
from multiprocessing.pool import ThreadPool
from random import random

import numpy as np
from matplotlib import pyplot as plt
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.core.duplicate import NoDuplicateElimination, ElementwiseDuplicateElimination, DuplicateElimination
from pymoo.core.mutation import Mutation
from pymoo.core.problem import Problem, ElementwiseProblem, StarmapParallelization
from pymoo.core.repair import Repair
from pymoo.core.sampling import Sampling
from pymoo.operators.crossover.ox import OrderCrossover
from pymoo.operators.crossover.pntx import TwoPointCrossover
from pymoo.operators.mutation.inversion import InversionMutation
from pymoo.operators.selection.rnd import RandomSelection
from pymoo.operators.selection.tournament import TournamentSelection
from pymoo.optimize import minimize
from pymoo.termination import get_termination

metadata = {}


def distance_between(a, b):
    global metadata
    return metadata['distance_matrix'][a][b]


def distance_delta_n2n(src_node, new_node, dst_node):
    return distance_between(src_node, new_node) + distance_between(new_node, dst_node) \
           - distance_between(src_node, dst_node)


def cheapest_insertion(route, src_donor_index, new_node):
    """ Donor to first node"""
    global metadata
    first_distance = distance_between(metadata['starts'][src_donor_index], new_node)
    if len(route) == 1:
        return 1, first_distance
    distances = [distance_delta_n2n(head, new_node, tail) for (head, tail) in window(route, 2)]

    min_distance = min(distances)
    return distances.index(min_distance) + 1, min_distance


def window(seq, n=2):
    "Returns a sliding window (of width n) over data from the iterable"
    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


class SimpleDuplicationElimination(ElementwiseDuplicateElimination):
    def is_equal(self, a, b):
        return np.array_equal(a.X, b.X)


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


class SwapMutation(Mutation):

    def _do(self, problem, X, **kwargs):
        for i in range(len(X)):
            r = np.random.random()

            # Swap two numbers (20% of the time)
            if r < 0.2:
                num_count = len(X[i])
                x1, x2 = np.random.randint(low=0, high=num_count, size=2)
                X[i][x1], X[i][x2] = X[i][x2], X[i][x1]

            p = np.random.random()
            # Swap two numbers on the same donor
            if p < 0.2:
                rem = X[i] // problem.algo_data['num_requests']
                donor_swap_index = np.random.randint(low=0, high=problem.algo_data['num_vehicles'])
                request_indices = np.where(rem == donor_swap_index)
                x1, x2 = np.random.choice(request_indices[0], size=2)
                X[i][x1], X[i][x2] = X[i][x2], X[i][x1]
        return X


class PermutationSequenceSampling(Sampling):
    def _do(self, problem, n_samples, **kwargs):
        samples = []
        for i in range(n_samples):
            samples.append(np.random.permutation(problem.n_var))
        return np.array(samples)


class DagasProblemParalellizedWrapper(ElementwiseProblem):
    def __init__(self, elementwise=True, algo_data=None, **kwargs):
        self.algo_data = algo_data
        super().__init__(elementwise, **kwargs)

    def chromosome_to_routes(self, chromosome) -> object:
        pass

    @staticmethod
    def fitness_func(routes, working_data):
        global metadata

        def get_total_weighted_demand(request_index):
            """This currently assumes all supply types are equally valuable"""
            return np.sum(metadata['demand_matrix'][request_index])

        demands = np.zeros(metadata['num_requests'])
        for request_ix in range(metadata['num_requests']):
            demands[request_ix] = get_total_weighted_demand(request_ix)
        total_demand = np.sum(demands)

        total_distance = 0
        max_distance = 0
        for route, start_node in zip(routes, metadata['starts']):
            # Initialize distance between donor and first evacuation node
            # Fitness 1: Total distance
            if len(route) == 0:
                continue
            route_distance = distance_between(start_node, route[0])
            for i, j in window(route):
                route_distance += distance_between(i, j)
            route_distance += distance_between(route[len(route) - 1], start_node)
            if route_distance > max_distance:
                max_distance = route_distance
            total_distance += route_distance

        # Fitness 2: Unmet demand
        unmet_demand = np.sum(working_data['demand_matrix'], axis=0)
        unmet_demand_ratio = unmet_demand / np.sum(metadata['demand_matrix'], axis=0)
        return total_distance, max_distance, *unmet_demand_ratio

    def _evaluate(self, x, out, *args, **kwargs):
        routes, working_data = self.chromosome_to_routes(x)
        out['F'] = np.array(self.fitness_func(routes, working_data))


class DagasGreedyDonorParallelizedWrapper(DagasProblemParalellizedWrapper):
    def __init__(self, elementwise=True, algo_data=None, **kwargs):
        lower_bound = np.zeros(algo_data['num_vehicles'])
        upper_bound = np.full(algo_data['num_vehicles'], algo_data['num_vehicles'] - 1)
        super().__init__(elementwise, algo_data,
                         n_var=algo_data['num_vehicles'], n_obj=2 + len(algo_data['item_types']),
                         xl=lower_bound, xu=upper_bound, **kwargs)

    def chromosome_to_routes(self, chromosome) -> object:
        global metadata
        routes = []

        working_data = copy.deepcopy(metadata)
        working_data['fulfillment_matrix'] = np.zeros((working_data['num_vehicles'],
                                                       working_data['num_requests'], len(working_data['item_types'])))

        def update_demand(req_ix, donor_ix):
            """Update current supply and demand based on chosen pair"""
            for type_index in range(len(working_data['item_types'])):
                current_supply = working_data['supply_matrix'][donor_ix][type_index]
                current_demand = working_data['demand_matrix'][req_ix][type_index]
                surplus = current_supply - current_demand
                working_data['fulfillment_matrix'][donor_ix, req_ix, type_index] += abs(surplus)
                if surplus >= 0:
                    working_data['demand_matrix'][req_ix][type_index] = 0
                    working_data['supply_matrix'][donor_ix][type_index] = surplus

                else:
                    working_data['demand_matrix'][req_ix][type_index] = abs(surplus)
                    working_data['supply_matrix'][donor_ix][type_index] = 0

        donor_request_counts = np.zeros(metadata['num_vehicles'])
        request_count = self.algo_data['num_requests']
        for i in range(metadata['num_vehicles']):
            routes.append([])
        # gene = Donor
        for gene in chromosome:
            if np.sum(working_data['supply_matrix'][gene]) == 0:
                continue
            donor_matrix_ix = gene + request_count
            current_node = donor_matrix_ix
            if np.sum(working_data['demand_matrix']) == 0:
                break
            explored_nodes = []
            while not np.sum(working_data['supply_matrix'][gene]) == 0:
                closest_requests = np.argsort(self.algo_data['distance_matrix'][current_node, :request_count - 1])
                if closest_requests[0] == current_node:
                    closest_requests = closest_requests[1:]
                for request_ix in closest_requests:
                    if not np.sum(working_data['demand_matrix'][request_ix]) == 0 \
                            and request_ix not in explored_nodes:
                        update_demand(request_ix, gene)
                        routes[gene].append(request_ix)
                        current_node = request_ix
                        explored_nodes.append(current_node)
                        break
        return routes, working_data


class DagasGreedParallelizedWrapper(DagasProblemParalellizedWrapper):

    def __init__(self, elementwise=True, algo_data=None, **kwargs):
        lower_bound = np.zeros(algo_data['num_requests'])
        upper_bound = np.full(algo_data['num_requests'], algo_data['num_requests'] - 1)
        super().__init__(elementwise, algo_data,
                         n_var=algo_data['num_requests'], n_obj=2 + len(algo_data['item_types']),
                         xl=lower_bound, xu=upper_bound, **kwargs)

    def chromosome_to_routes(self, chromosome) -> object:
        global metadata
        routes = []

        working_data = copy.deepcopy(metadata)
        working_data['fulfillment_matrix'] = np.zeros((working_data['num_vehicles'],
                                                       working_data['num_requests'], len(working_data['item_types'])))

        def update_gene_demand(gene_index, donor_ix):
            """Update current supply and demand based on chosen pair"""
            for type_index in range(len(working_data['item_types'])):
                current_supply = working_data['supply_matrix'][donor_ix][type_index]
                current_demand = working_data['demand_matrix'][gene_index][type_index]
                surplus = current_supply - current_demand
                working_data['fulfillment_matrix'][donor_ix, gene_index, type_index] += abs(surplus)
                if surplus >= 0:
                    working_data['demand_matrix'][gene_index][type_index] = 0
                    working_data['supply_matrix'][donor_ix][type_index] = surplus

                else:
                    working_data['demand_matrix'][gene_index][type_index] = abs(surplus)
                    working_data['supply_matrix'][donor_ix][type_index] = 0

        donor_request_counts = np.zeros(metadata['num_vehicles'])
        request_count = self.algo_data['num_requests']
        for i in range(metadata['num_vehicles']):
            routes.append([])
        for gene in chromosome:
            if np.sum(working_data['demand_matrix'][gene]) == 0:
                continue
            closest_donor = np.argmin(self.algo_data['distance_matrix'][request_count:, gene])
            routes[closest_donor].append(gene)
            update_gene_demand(gene, closest_donor)
            closest_donor_matrix_ix = request_count + closest_donor
            closest_requests = np.argsort(self.algo_data['distance_matrix']
                                          [closest_donor_matrix_ix, :request_count - 1])
            for request_ix in closest_requests:
                if np.sum(working_data['supply_matrix'][closest_donor]) == 0:
                    break
                update_gene_demand(request_ix, closest_donor)
                routes[closest_donor].append(request_ix)
        return routes, working_data


class DagasDenseParallelizedWrapper(DagasProblemParalellizedWrapper):

    def __init__(self, elementwise=True, algo_data=None, **kwargs):
        chromosome_length = algo_data['num_requests'] * algo_data['num_vehicles']
        lower_bound = np.zeros(chromosome_length)
        upper_bound = np.full(chromosome_length, chromosome_length - 1)
        super().__init__(elementwise, algo_data,
                         n_var=chromosome_length, n_obj=2 + len(algo_data['item_types']),
                         xl=lower_bound, xu=upper_bound, **kwargs)

    def chromosome_to_routes(self, chromosome) -> object:
        global metadata
        routes = []
        for i in range(metadata['num_vehicles']):
            routes.append([])
        working_data = copy.deepcopy(metadata)
        for gene in chromosome:
            donor_index = gene // working_data['num_requests']
            request_index = gene % working_data['num_requests']
            if np.sum(working_data['supply_matrix']) == 0 or np.sum(working_data['demand_matrix']) == 0:
                break
            if np.sum(working_data['supply_matrix'][donor_index]) == 0 \
                    or np.sum(working_data['demand_matrix'][request_index]) == 0:
                continue
            for type_index in range(len(working_data['item_types'])):
                current_supply = working_data['supply_matrix'][donor_index][type_index]
                current_demand = working_data['demand_matrix'][request_index][type_index]
                surplus = current_supply - current_demand
                if surplus >= 0:
                    working_data['demand_matrix'][request_index][type_index] = 0
                    working_data['supply_matrix'][donor_index][type_index] = surplus

                else:
                    working_data['demand_matrix'][request_index][type_index] = abs(surplus)
                    working_data['supply_matrix'][donor_index][type_index] = 0
            routes[donor_index].append(request_index)
        return routes, working_data


# class DagasProblemWrapper(Problem):
#     def _evaluate(self, X, out, *args, **kwargs):
#         results = []
#         for solution in X:
#             routes, working_data = chromosome_to_routes(solution)
#             results.append(fitness_func(routes, working_data))
#         out['F'] = np.array(results)


def run_ga_algo(data):
    global metadata
    metadata = data
    # Parallelization Configuration
    n_threads = 20
    pool = ThreadPool(n_threads)
    runner = StarmapParallelization(pool.starmap)

    problem = DagasDenseParallelizedWrapper(algo_data=data, elementwise_runner=runner)
    algorithm = NSGA2(pop_size=100,
                      sampling=PermutationSequenceSampling(),
                      crossover=OrderCrossover(),
                      mutation=InversionMutation(),
                      # repair=RepetitionRepair(),
                      # eliminate_duplicates=NoDuplicateElimination(),
                      eliminate_duplicates=SimpleDuplicationElimination()
                      )
    terminating_condition = get_termination('n_gen', 1000, )
    res = minimize(
        problem=problem,
        algorithm=algorithm,
        termination=terminating_condition,
        seed=1,
        verbose=True,
    )
    print(res.F)
    return res, problem
