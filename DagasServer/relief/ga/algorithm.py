import copy
import sys
from itertools import islice
from multiprocessing.pool import ThreadPool
from random import random

import numpy as np
from matplotlib import pyplot as plt
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.duplicate import NoDuplicateElimination, ElementwiseDuplicateElimination, DuplicateElimination
from pymoo.core.mutation import Mutation
from pymoo.core.problem import Problem, ElementwiseProblem, StarmapParallelization
from pymoo.core.repair import Repair
from pymoo.core.sampling import Sampling
from pymoo.operators.crossover.pntx import TwoPointCrossover
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


def chromosome_to_routes(chromosome):
    global metadata
    routes = []

    working_data = copy.deepcopy(metadata)

    def is_gene_complete(gene_index):
        demand_remaining = np.sum(working_data['demand_matrix'][gene_index])
        return demand_remaining == 0

    def complete_supply_remaining(donor_ix):
        supply_remaining = 0
        supply_remaining = np.sum(working_data['supply_matrix'][donor_ix])
        return supply_remaining

    def is_donor_done(donor_ix):
        return complete_supply_remaining(donor_ix) == 0

    def update_gene_demand(gene_index, donor_ix):
        """Update current supply and demand based on chosen pair"""
        for type_index in range(len(working_data['item_types'])):
            current_supply = working_data['supply_matrix'][donor_ix][type_index]
            current_demand = working_data['demand_matrix'][gene_index][type_index]
            surplus = current_supply - current_demand
            if surplus >= 0:
                working_data['demand_matrix'][gene_index][type_index] = 0
                working_data['supply_matrix'][donor_ix][type_index] = surplus

            else:
                working_data['demand_matrix'][gene_index][type_index] = abs(surplus)
                working_data['supply_matrix'][donor_ix][type_index] = 0

    def supply_out():
        """Check if all donors are out of supplies"""
        total_supply_remaining = 0
        for donor_ix in range(working_data['num_vehicles']):
            total_supply_remaining += complete_supply_remaining(donor_ix)
        return total_supply_remaining == 0

    donor_request_counts = np.zeros(metadata['num_vehicles'])
    for i in range(metadata['num_vehicles']):
        routes.append([])
    for gene in chromosome:

        # TODO: Consider implementing donor request or distance limits
        while not is_gene_complete(gene) and not supply_out():
            min_add_distance = sys.maxsize
            chosen_donor = None
            chosen_position = None
            for donor_index in range(metadata['num_vehicles']):

                donor_route = routes[donor_index]
                if is_donor_done(donor_index) or gene in donor_route:
                    continue
                if len(donor_route) == 0:
                    if distance_between(donor_index, gene) < min_add_distance:
                        min_add_distance = distance_between(donor_index, gene)
                        chosen_donor = donor_index
                        chosen_position = 0
                else:
                    index, cheapest_distance = cheapest_insertion(donor_route, donor_index, gene)
                    if cheapest_distance < min_add_distance:
                        min_add_distance = cheapest_distance
                        chosen_donor = donor_index
                        chosen_position = index
            if chosen_donor is None:
                break
            routes[chosen_donor].insert(chosen_position, gene)
            update_gene_demand(gene, chosen_donor)
    return routes, working_data


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


def fitness_func(routes, working_data):
    # Iterate through every donor
    global metadata

    def get_total_weighted_demand(request_index):
        """This currently assumes all supply types are equally valuable"""
        return np.sum(metadata['demand_matrix'][request_index])

    demands = np.zeros(metadata['num_requests'])
    for request_ix in range(metadata['num_requests']):
        demands[request_ix] = get_total_weighted_demand(request_ix)
    total_demand = np.sum(demands)

    total_distance = 0
    for route, start_node in zip(routes, metadata['starts']):
        # Initialize distance between donor and first evacuation node
        # Fitness 1: Total distance
        if len(route) == 0:
            continue
        route_distance = distance_between(start_node, route[0])
        for i, j in window(route):
            route_distance += distance_between(i, j)
        route_distance += distance_between(route[len(route) - 1], start_node)
        total_distance += route_distance

    # Fitness 2: Unmet demand
    unmet_demand = np.sum(working_data['demand_matrix'], axis=0)
    unmet_demand_ratio = unmet_demand / np.sum(metadata['demand_matrix'], axis=0)
    return total_distance, *unmet_demand_ratio


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

        return X


class PermutationSequenceSampling(Sampling):
    def _do(self, problem, n_samples, **kwargs):
        samples = []
        for i in range(n_samples):
            samples.append(np.random.permutation(problem.n_var))
        return np.array(samples)


class DagasProblemParalellizedWrapper(ElementwiseProblem):
    def _evaluate(self, x, out, *args, **kwargs):
        routes, working_data = chromosome_to_routes(x)
        out['F'] = np.array(fitness_func(routes, working_data))


class DagasProblemWrapper(Problem):
    def _evaluate(self, X, out, *args, **kwargs):
        results = []
        for solution in X:
            routes, working_data = chromosome_to_routes(solution)
            results.append(fitness_func(routes, working_data))
        out['F'] = np.array(results)


def run_ga_algo(data):
    global metadata
    metadata = data
    # Parallelization Configuration
    n_threads = 20
    pool = ThreadPool(n_threads)
    runner = StarmapParallelization(pool.starmap)
    lower_bound = np.zeros(data['num_requests'])
    upper_bound = np.full(data['num_requests'], data['num_requests'] - 1)

    problem = DagasProblemParalellizedWrapper(n_var=data['num_requests'], n_obj=1 + len(data['item_types']),
                                              xl=lower_bound, xu=upper_bound,
                                              elementwise_runner=runner)
    algorithm = NSGA2(pop_size=100,
                      sampling=PermutationSequenceSampling(),
                      crossover=TwoPointCrossover(),
                      mutation=SwapMutation(),
                      repair=RepetitionRepair(),
                      eliminate_duplicates=SimpleDuplicationElimination()
                      )
    terminating_condition = get_termination('n_gen', 100, )
    res = minimize(
        problem=problem,
        algorithm=algorithm,
        termination=terminating_condition,
        seed=1,
        verbose=True,
    )
    print(res.F)
    return res
