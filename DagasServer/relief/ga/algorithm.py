import copy
import sys
from itertools import islice
from multiprocessing.pool import ThreadPool

import numpy as np
from numpy import uint8
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import ElementwiseProblem, StarmapParallelization
from pymoo.operators.crossover.ox import OrderCrossover
from pymoo.operators.mutation.inversion import InversionMutation
from pymoo.optimize import minimize
from pymoo.termination import get_termination

from relief.ga.dupl_elim import SimpleDuplicationElimination
from relief.ga.mutation import SwapMutation
from relief.ga.repair import RepetitionRepair
from relief.ga.sampling import PermutationSequenceSampling, PermutationCombinedRouteSampling, ClosestDepotSampling, \
    ClosestDenseDepotSampling, ClosestSoloDepotSampling

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


class DagasProblemParalellizedWrapper(ElementwiseProblem):
    def __init__(self, elementwise=True, algo_data=None, **kwargs):
        self.algo_data = algo_data
        super().__init__(elementwise, **kwargs)

    def chromosome_to_routes(self, chromosome) -> object:
        pass

    def fitness_func(self, routes, working_data):
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


class DagasSoloProblemParalellizedWrapper(DagasProblemParalellizedWrapper):
    def __init__(self, elementwise=True, algo_data=None, **kwargs):
        chromosome_length = algo_data['num_requests']
        algo_data['total_demands'] = np.sum(algo_data['demand_matrix'], axis=0)
        algo_data['complete_total_demands'] = np.sum(algo_data['total_demands'])
        algo_data['total_supplies'] = np.sum(algo_data['supply_matrix'])
        lower_bound = np.zeros(chromosome_length)
        upper_bound = np.full(chromosome_length, chromosome_length - 1)
        super().__init__(elementwise, algo_data,
                         n_var=chromosome_length, n_obj=1 + len(algo_data['item_types']),
                         xl=lower_bound, xu=upper_bound, **kwargs)

    def chromosome_to_routes(self, chromosome) -> object:
        # global metadata
        # route = []
        route = []

        # working_data = copy.deepcopy(data)
        working_data = self.algo_data
        total_remaining_supplies = working_data['total_supplies']
        complete_total_demands = working_data['complete_total_demands']
        total_demands = np.sum(working_data['demand_matrix'], axis=0)
        supplied_demands = np.zeros(len(working_data['item_types']))
        for node in chromosome:
            remaining_supplies = working_data['supply_matrix'] - supplied_demands
            # remaining_demands = total_demands - supplied_demands
            if total_remaining_supplies == 0 or complete_total_demands == 0:
                break

            # if np.sum(working_data['supply_matrix']) == 0 \
            #         or np.sum(working_data['demand_matrix'][node]) == 0:
            #     continue
            for type_index in range(len(working_data['item_types'])):
                current_supply = remaining_supplies[type_index]
                current_demand = working_data['demand_matrix'][node][type_index]
                surplus = current_supply - current_demand

                if surplus >= 0:
                    supplied_demands[type_index] += current_demand
                    total_remaining_supplies -= current_demand
                    complete_total_demands -= current_demand

                else:
                    supplied_demands[type_index] += current_supply
                    total_remaining_supplies -= current_supply
                    complete_total_demands -= current_supply
            route.append(node)
        return route, working_data

    def fitness_func(self, route, working_data):
        global metadata

        def get_total_weighted_demand(request_index):
            """This currently assumes all supply types are equally valuable"""
            return np.sum(metadata['demand_matrix'][request_index])

        demands = np.zeros(metadata['num_requests'])
        for request_ix in range(metadata['num_requests']):
            demands[request_ix] = get_total_weighted_demand(request_ix)

        total_distance = 0
        max_distance = 0
        # Initialize distance between donor and first evacuation node
        # Fitness 1: Total distance
        start_node = working_data['starts'][0]
        route_distance = distance_between(start_node, route[0])
        for i, j in window(route):
            route_distance += distance_between(i, j)
        route_distance += distance_between(route[len(route) - 1], start_node)
        if route_distance > max_distance:
            total_distance += route_distance

        # Fitness 2: Unmet demand
        unmet_demand = np.sum(working_data['demand_matrix'], axis=0)
        unmet_demand_ratio = unmet_demand / np.sum(metadata['demand_matrix'], axis=0)
        return total_distance, *unmet_demand_ratio


class DagasSequenceParalellizedWrapper(DagasProblemParalellizedWrapper):
    MARKER = -1

    def __init__(self, elementwise=True, algo_data=None, **kwargs):
        chromosome_length = algo_data['num_requests'] + algo_data['num_vehicles'] - 1
        lower_bound = np.zeros(chromosome_length)
        upper_bound = np.full(chromosome_length, chromosome_length - 1)
        super().__init__(elementwise, algo_data,
                         n_var=chromosome_length, n_obj=2 + len(algo_data['item_types']),
                         xl=lower_bound, xu=upper_bound, **kwargs)

    def distance_n2n(self, src_node, dst_node):
        return self.algo_data['distance_matrix'][src_node][dst_node]

    def distance_delta_n2n(self, src_node, new_node, dst_node):
        return self.distance_n2n(src_node, new_node) + self.distance_n2n(new_node, dst_node) \
               - self.distance_n2n(src_node, dst_node)

    def cheapest_insertion(self, route, src_donor_index, new_node):
        """ Donor to first node"""

        first_distance = self.distance_n2n(self.algo_data['starts'][src_donor_index], new_node)
        if len(route) == 1 or len(route) == 0:
            return len(route), first_distance
        distances = [self.distance_delta_n2n(head, new_node, tail) for (head, tail) in window(route, 2)]

        min_distance = min(distances)
        return distances.index(min_distance) + 1, min_distance

    def chromosome_to_routes(self, chromosome) -> object:
        global metadata
        routes = []
        for i in range(metadata['num_vehicles']):
            routes.append([])
        working_data = copy.deepcopy(metadata)
        # a = np.where(chromosome >= -1)
        pseudo_routes = np.split(chromosome, np.where(chromosome >= self.algo_data['num_requests'])[0])
        working_data['fulfillment_matrix'] = np.zeros((working_data['num_vehicles'],
                                                       working_data['num_requests'], len(working_data['item_types'])))
        request_count = self.algo_data['num_requests']
        unfinished_requests = np.array([])

        def update_demand(req_ix, d_ix):
            """Update current supply and demand based on chosen pair"""
            for type_index in range(len(working_data['item_types'])):
                current_supply = working_data['supply_matrix'][d_ix][type_index]
                current_demand = working_data['demand_matrix'][req_ix][type_index]
                surplus = current_supply - current_demand
                working_data['fulfillment_matrix'][d_ix, req_ix, type_index] += abs(surplus)
                if surplus >= 0:
                    working_data['demand_matrix'][req_ix][type_index] = 0
                    working_data['supply_matrix'][d_ix][type_index] = surplus

                else:
                    working_data['demand_matrix'][req_ix][type_index] = abs(surplus)
                    working_data['supply_matrix'][d_ix][type_index] = 0

        for current_donor_ix, pseudo_route in enumerate(pseudo_routes):
            donor_matrix_ix = current_donor_ix + request_count
            current_node = donor_matrix_ix
            explored_nodes = []
            pseudo_route = pseudo_route[pseudo_route < request_count]
            if np.sum(working_data['supply_matrix'][current_donor_ix]) == 0:
                continue
            if np.sum(working_data['demand_matrix']) == 0:
                break
            while not np.sum(working_data['supply_matrix'][current_donor_ix]) == 0 \
                    and not len(pseudo_route) == 0:
                closest_requests_ix = np.argsort(self.algo_data['distance_matrix'][current_node, pseudo_route])
                closest_requests = pseudo_route[closest_requests_ix]

                for request_ix in closest_requests:
                    if not np.sum(working_data['demand_matrix'][request_ix]) == 0:
                        update_demand(request_ix, current_donor_ix)
                        routes[current_donor_ix].append(request_ix)
                        current_node = request_ix
                        pseudo_route = np.delete(pseudo_route, np.argwhere(pseudo_route == current_node))
                        break
        unfinished_requests = np.where(np.sum(working_data['demand_matrix'], axis=1) > 0)[0]
        for _ in unfinished_requests:
            cheapest_insertion_distance = sys.maxsize
            cheapest_donor_ix = None
            cheapest_position_ix = None
            cheapest_request_ix = None
            for donor_ix in range(self.algo_data['num_vehicles']):
                if np.sum(working_data['supply_matrix'][donor_ix] == 0):
                    continue
                for request_ix in unfinished_requests:
                    if np.sum(working_data['demand_matrix'][request_ix]) == 0:
                        unfinished_requests = np.delete(unfinished_requests,
                                                        np.argwhere(unfinished_requests == request_ix))
                        continue

                    position_ix, distance = self.cheapest_insertion(routes[donor_ix],
                                                                    donor_ix,
                                                                    request_ix)
                    if cheapest_insertion_distance > distance:
                        cheapest_insertion_distance = distance
                        cheapest_position_ix = position_ix
                        cheapest_request_ix = request_ix
                        cheapest_donor_ix = donor_ix
            if cheapest_donor_ix is not None:
                routes[cheapest_donor_ix].insert(cheapest_position_ix, cheapest_request_ix)
                update_demand(cheapest_request_ix, cheapest_donor_ix)
                if np.sum(working_data['demand_matrix'][cheapest_request_ix]) == 0:
                    unfinished_requests = np.delete(unfinished_requests,
                                                    np.argwhere(unfinished_requests == cheapest_request_ix))

        # working_data['unvisited_requests'] = np.where(np.sum(working_data['demand_matrix'], axis=1))
        return routes, working_data


class DagasMDVRPFDStyleParallelizedWrapper(DagasProblemParalellizedWrapper):
    def __init__(self, elementwise=True, algo_data=None, **kwargs):
        lower_bound = np.zeros(algo_data['num_requests'])
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


class DagasLNNHDonorParallelizedWrapper(DagasProblemParalellizedWrapper):
    def __init__(self, elementwise=True, algo_data=None, n_neighbors=3, **kwargs):
        self.n_neighbors = n_neighbors
        lower_bound = np.zeros(algo_data['num_vehicles'])
        upper_bound = np.full(algo_data['num_vehicles'], algo_data['num_vehicles'] - 1)
        super().__init__(elementwise, algo_data,
                         n_var=algo_data['num_vehicles'], n_obj=2 + len(algo_data['item_types']),
                         xl=lower_bound, xu=upper_bound, **kwargs)

    def distance_between(self, a, b):
        return self.algo_data['distance_matrix'][a][b]

    def chromosome_to_routes(self, chromosome) -> object:
        global metadata
        routes = []

        working_data = copy.deepcopy(metadata)
        working_data['fulfillment_matrix'] = np.zeros((working_data['num_vehicles'],
                                                       working_data['num_requests'], len(working_data['item_types'])))

        def check_resulting_supply(supplies, req_ix):
            """Update current supply and demand based on chosen pair"""
            new_supplies = np.copy(supplies)
            for type_index in range(len(working_data['item_types'])):
                current_supply = supplies[type_index]
                current_demand = working_data['demand_matrix'][req_ix][type_index]
                surplus = current_supply - current_demand
                if surplus >= 0:
                    new_supplies[type_index] = surplus
                else:
                    new_supplies[type_index] = 0
            return new_supplies

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
            current_supplies = working_data['supply_matrix'][gene]
            while not np.sum(working_data['supply_matrix'][gene]) == 0:
                closest_requests = np.argsort(self.algo_data['distance_matrix'][current_node, :request_count])
                closest_requests = closest_requests[closest_requests != current_node]
                a = np.isin(closest_requests, routes[gene])
                closest_requests = closest_requests[np.logical_not(np.isin(closest_requests, routes[gene]))]
                unfinished_requests = np.where(np.sum(self.algo_data['demand_matrix'][closest_requests], axis=1) != 0)
                unfinished_closest_requests = closest_requests[unfinished_requests]
                cheapest_distance = sys.maxsize
                cheapest_neighbors = None
                neighbor_layer_1 = unfinished_closest_requests[:self.n_neighbors]
                for neighbor_ix in neighbor_layer_1:
                    resulting_supply = check_resulting_supply(current_supplies, neighbor_ix)
                    if np.sum(resulting_supply) == 0:
                        if distance_between(current_node, neighbor_ix) < cheapest_distance:
                            cheapest_distance = distance_between(current_node, neighbor_ix)
                            cheapest_neighbors = [neighbor_ix]
                        continue
                    neighbor_closest_requests = np.argsort(self.algo_data['distance_matrix'][neighbor_ix,
                                                           :request_count])
                    neighbor_closest_requests = neighbor_closest_requests[np.logical_and(
                        neighbor_closest_requests != current_node,
                        neighbor_closest_requests != neighbor_ix)]
                    # np.logical_not(np.isin(closest_requests, routes[gene]))
                    neighbor_closest_requests = neighbor_closest_requests[np.logical_not(
                        np.isin(neighbor_closest_requests, routes[gene]))]
                    unfinished_neighbor_requests = np.where(np.sum(
                        self.algo_data['demand_matrix'][neighbor_closest_requests], axis=1) != 0)
                    unfinished_closest_neighbor_requests = neighbor_closest_requests[unfinished_neighbor_requests]
                    neighbor_layer_2 = unfinished_closest_neighbor_requests[:self.n_neighbors]
                    for neighbor_ix_2 in neighbor_layer_2:
                        distance = distance_between(current_node, neighbor_ix) + distance_between(neighbor_ix,
                                                                                                  neighbor_ix_2)
                        if distance < cheapest_distance:
                            cheapest_distance = distance
                            cheapest_neighbors = [neighbor_ix, neighbor_ix_2]
                for cheap_neighbor in cheapest_neighbors:
                    routes[gene].append(cheap_neighbor)
                    update_demand(cheap_neighbor, gene)
        return routes, working_data


class DagasNNHDonorParallelizedWrapper(DagasProblemParalellizedWrapper):
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


class DagasGreedyNeighborParallelizedWrapper(DagasProblemParalellizedWrapper):

    def __init__(self, elementwise=True, algo_data=None, **kwargs):
        lower_bound = np.zeros(algo_data['num_requests'])
        upper_bound = np.full(algo_data['num_requests'], algo_data['num_requests'] - 1)
        super().__init__(elementwise, algo_data,
                         n_var=algo_data['num_requests'], n_obj=2 + len(algo_data['item_types']),
                         xl=lower_bound, xu=upper_bound, **kwargs)

    def distance_n2n(self, src_node, dst_node):
        return self.algo_data['distance_matrix'][src_node][dst_node]

    def distance_delta_n2n(self, src_node, new_node, dst_node):
        return self.distance_n2n(src_node, new_node) + self.distance_n2n(new_node, dst_node) \
               - self.distance_n2n(src_node, dst_node)

    def cheapest_insertion(self, route, src_donor_index, new_node):
        """ Donor to first node"""

        first_distance = self.distance_n2n(self.algo_data['starts'][src_donor_index], new_node)
        if len(route) == 1 or len(route) == 0:
            return len(route), first_distance
        distances = [distance_delta_n2n(head, new_node, tail) for (head, tail) in window(route, 2)]

        min_distance = min(distances)
        return distances.index(min_distance) + 1, min_distance

    def chromosome_to_routes(self, chromosome) -> object:
        global metadata
        routes = []

        working_data = copy.deepcopy(metadata)
        working_data['fulfillment_matrix'] = np.zeros((working_data['num_vehicles'],
                                                       working_data['num_requests'], len(working_data['item_types'])))

        def update_gene_demand(gene_index, d_ix):
            """Update current supply and demand based on chosen pair"""
            for type_index in range(len(working_data['item_types'])):
                current_supply = working_data['supply_matrix'][d_ix][type_index]
                current_demand = working_data['demand_matrix'][gene_index][type_index]
                surplus = current_supply - current_demand
                working_data['fulfillment_matrix'][d_ix, gene_index, type_index] += abs(surplus)
                if surplus >= 0:
                    working_data['demand_matrix'][gene_index][type_index] = 0
                    working_data['supply_matrix'][d_ix][type_index] = surplus

                else:
                    working_data['demand_matrix'][gene_index][type_index] = abs(surplus)
                    working_data['supply_matrix'][d_ix][type_index] = 0

        donor_request_counts = np.zeros(metadata['num_vehicles'])
        request_count = self.algo_data['num_requests']
        for i in range(metadata['num_vehicles']):
            routes.append([])
        for gene in chromosome:
            if np.sum(working_data['demand_matrix'][gene]) == 0:
                continue
            closest_donors = np.argsort(self.algo_data['distance_matrix'][request_count:, gene])
            closest_donor = None
            for donor_ix in closest_donors:
                if not np.sum(working_data['supply_matrix'][donor_ix]) == 0:
                    closest_donor = donor_ix
                    break

            if closest_donor is None:
                continue
            routes[closest_donor].append(gene)
            update_gene_demand(gene, closest_donor)
            closest_donor_matrix_ix = request_count + closest_donor

            # closest_requests = np.argsort(self.algo_data['distance_matrix']
            #                               [closest_donor_matrix_ix, :request_count - 1])
            # Generate immediate neighbors

            # cheapest_insertion_distance = sys.maxsize
            # cheapest_position_ix = None
            # cheapest_request_ix = None
            # for request_ix in range(request_count):
            #     if np.sum(working_data['demand_matrix'][request_ix]) == 0:
            #         continue
            #     position_ix, distance = self.cheapest_insertion(routes[closest_donor],
            #                                                     closest_donor,
            #                                                     request_ix)
            #     if cheapest_insertion_distance > distance:
            #         cheapest_insertion_distance = distance
            #         cheapest_position_ix = position_ix
            #         cheapest_request_ix = request_ix
            # if cheapest_request_ix is not None:
            #     update_gene_demand(cheapest_request_ix, closest_donor)
            #     # routes[closest_donor].append(request_ix)
            #     routes[closest_donor].insert(cheapest_position_ix, cheapest_request_ix)
            # routes[closest_donor].insert(cheapest_position_ix, cheapest_request_ix)
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


def run_solo_ga_algo(data):
    global metadata
    metadata = data
    # Parallelization Configuration
    n_threads = 20
    pool = ThreadPool(n_threads)
    runner = StarmapParallelization(pool.starmap)

    problem = DagasSoloProblemParalellizedWrapper(algo_data=data, elementwise_runner=runner)
    algorithm = NSGA2(pop_size=100,
                      sampling=ClosestSoloDepotSampling(),  # PermutationSequenceSampling for other algos
                      crossover=OrderCrossover(),
                      mutation=InversionMutation(),
                      # repair=RepetitionRepair(), # Disabled for DagasSequenceParallelizedWrapper
                      # eliminate_duplicates=NoDuplicateElimination(),
                      eliminate_duplicates=SimpleDuplicationElimination()
                      )

    terminating_condition = get_termination('n_gen', 100, )
    res = minimize(
        problem=problem,
        algorithm=algorithm,
        termination=terminating_condition,
        seed=2,
        verbose=True,
    )
    print(res.F)
    return res, problem


def run_ga_algo(data):
    global metadata
    metadata = data
    # Parallelization Configuration
    n_threads = 20
    pool = ThreadPool(n_threads)
    runner = StarmapParallelization(pool.starmap)

    problem = DagasNNHDonorParallelizedWrapper(algo_data=data, elementwise_runner=runner, n_neighbors=3)
    algorithm = NSGA2(pop_size=100,
                      sampling=PermutationSequenceSampling(),  # PermutationSequenceSampling for other algos
                      crossover=OrderCrossover(),
                      mutation=InversionMutation(),
                      # repair=RepetitionRepair(), # Disabled for DagasSequenceParallelizedWrapper
                      # eliminate_duplicates=NoDuplicateElimination(),
                      eliminate_duplicates=SimpleDuplicationElimination()
                      )
    # problem = DagasDenseParallelizedWrapper(algo_data=data, elementwise_runner=runner)
    # algorithm = NSGA2(pop_size=100,
    #                   sampling=ClosestDenseDepotSampling(),  # PermutationSequenceSampling for other algos
    #                   crossover=OrderCrossover(),
    #                   mutation=SwapMutation(),
    #                   # repair=RepetitionRepair(), # Disabled for DagasSequenceParallelizedWrapper
    #                   # eliminate_duplicates=NoDuplicateElimination(),
    #                   eliminate_duplicates=SimpleDuplicationElimination()
    #                   )
    # algorithm = NSGA2(pop_size=100,
    #                   sampling=ClosestDepotSampling(),  # PermutationSequenceSampling for other algos
    #                   crossover=OrderCrossover(),
    #                   mutation=InversionMutation(),
    #                   # repair=RepetitionRepair(), # Disabled for DagasSequenceParallelizedWrapper
    #                   # eliminate_duplicates=NoDuplicateElimination(),
    #                   eliminate_duplicates=SimpleDuplicationElimination()
    #                   )
    terminating_condition = get_termination('n_gen', 100, )
    res = minimize(
        problem=problem,
        algorithm=algorithm,
        termination=terminating_condition,
        seed=4,
        verbose=True,
    )
    print(res.F)
    return res, problem
