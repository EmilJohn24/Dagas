import copy
import random
from itertools import islice

import numpy as np


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


def initial_solution(data):
    samples = []
    request_count = data['num_requests']
    distance_matrix_d2r = data['distance_matrix']
    current_node = data['starts'][0]  # Donor
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
    return np.array(route)


def distance_between(data, a, b):
    return data['distance_matrix'][a][b]


def fitness_func(data, route):
    # working_data = copy.deepcopy(data)
    # def get_total_weighted_demand(request_index):
    #     """This currently assumes all supply types are equally valuable"""
    #     return np.sum(working_data['demand_matrix'][request_index])
    #
    # demands = np.zeros(working_data['num_requests'])
    # for request_ix in range(working_data['num_requests']):
    #     demands[request_ix] = get_total_weighted_demand(request_ix)
    #
    # total_distance = 0
    # max_distance = 0
    # Initialize distance between donor and first evacuation node
    # Fitness 1: Total distance
    if len(route) == 0:
        return 0
    start_node = data['starts'][0]
    route_distance = distance_between(data, start_node, route[0])
    for i, j in window(route):
        route_distance += distance_between(data, i, j)
    route_distance += distance_between(data, route[len(route) - 1], start_node)
    return route_distance
    # if route_distance > max_distance:
    #     total_distance += route_distance

    # Fitness 2: Unmet demand
    # unmet_demand = np.sum(working_data['demand_matrix'], axis=0)
    # unmet_demand_ratio = unmet_demand / np.sum(data['demand_matrix'], axis=0)


def solution_to_route(solution, data, is_final=False):
    route = []

    # working_data = copy.deepcopy(data)
    working_data = data
    total_demands = np.sum(working_data['demand_matrix'], axis=0)
    supplied_demands = np.zeros(len(working_data['item_types']))
    if is_final:
        working_data['fulfillment_matrix'] = np.zeros((working_data['num_requests'], len(working_data['item_types'])))
    for node in solution:
        remaining_supplies = working_data['supply_matrix'] - supplied_demands
        remaining_demands = total_demands - supplied_demands
        if np.sum(remaining_supplies) == 0 or np.sum(remaining_demands) == 0:
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
                if is_final:
                    working_data['fulfillment_matrix'][node, type_index] += current_demand

            else:
                supplied_demands[type_index] += current_supply
                if is_final:
                    working_data['fulfillment_matrix'][node, type_index] += current_supply
        route.append(node)
    return np.array(route), len(route), working_data


def generate_neighbors(data, solution, route_len):
    visited_nodes = solution[0:route_len].copy()
    unvisited_nodes = solution[route_len:].copy()
    neighbors = []

    for _ in range(100):
        # Operator 1: insert unvisited to visited (preferably non-uniform distribution)
        if not len(unvisited_nodes) == 0:
            visited_nodes = solution[0:route_len].copy()
            unvisited_nodes = solution[route_len:].copy()
            random_unvisited_ix = np.random.choice(range(len(unvisited_nodes)), 1)
            random_unvisited = unvisited_nodes[random_unvisited_ix]
            unvisited_nodes = np.delete(unvisited_nodes, random_unvisited_ix)
            visited_nodes = np.insert(visited_nodes, np.random.randint(0, len(visited_nodes)), random_unvisited)
            neighbors.append(np.concatenate([visited_nodes, unvisited_nodes]))
        # Operator 2: remove visited
        if not len(unvisited_nodes) == 0:
            visited_nodes = solution[0:route_len].copy()
            unvisited_nodes = solution[route_len:].copy()
            random_visited_ix = np.random.choice(range(len(visited_nodes)), 1)
            random_visited = visited_nodes[random_visited_ix]
            visited_nodes = np.delete(visited_nodes, random_visited_ix)
            unvisited_nodes = np.insert(unvisited_nodes, np.random.randint(0, len(unvisited_nodes)), random_visited)
            neighbors.append(np.concatenate([visited_nodes, unvisited_nodes]))
        visited_nodes = solution[0:route_len].copy()
        unvisited_nodes = solution[route_len:].copy()
        # Operator 3: Swap two visited nodes
        if (len(visited_nodes) > 1):
            num_count = len(visited_nodes)
            x1, x2 = random.sample(range(num_count), 2)
            visited_nodes[x1], visited_nodes[x2] = visited_nodes[x2], visited_nodes[x1]
            neighbors.append(np.concatenate([visited_nodes, unvisited_nodes]))

            visited_nodes = solution[0:route_len].copy()
            unvisited_nodes = solution[route_len:].copy()
            # Operator 4: Move visited into another visited position
            random_visited_ix, new_position_ix = random.sample(range(len(visited_nodes)), 2)
            # random_visited_ix = np.random.choice(range(len(visited_nodes)), 1)
            random_visited = visited_nodes[random_visited_ix]
            visited_nodes = np.delete(visited_nodes, random_visited_ix)
            visited_nodes = np.insert(visited_nodes, new_position_ix, random_visited)
            neighbors.append(np.concatenate([visited_nodes, unvisited_nodes]))

            # Operator 5: 2-opt (Subroute inversion)
            visited_nodes = solution[0:route_len].copy()
            unvisited_nodes = solution[route_len:].copy()
            point_a, point_b = random.sample(range(len(visited_nodes)), 2)
            if point_a < point_b:
                visited_nodes[point_a:point_b] = visited_nodes[point_a:point_b][::-1]
            else:
                visited_nodes[point_b:point_a] = visited_nodes[point_b:point_a][::-1]
            neighbors.append(np.concatenate([visited_nodes, unvisited_nodes]))
    return neighbors


def is_in_tabu(route, tabu_list):
    for tabu_route in tabu_list:
        if np.array_equal(tabu_route, route):
            return True
    return False


def tabu_algorithm(data):
    init_sol = initial_solution(data)
    route, route_len, _ = solution_to_route(init_sol, data)
    best_sol = init_sol.copy()
    best_candidate = best_sol.copy()
    best_candidate_route_len = route_len
    best_distance = fitness_func(data, route)
    tabu_list = [route]
    max_tabu_size = 100
    for iteration in range(100):
        # neighbors = generate_neighbors(data, best_sol, best_sol_route_len)
        neighbors = generate_neighbors(data, best_candidate, best_candidate_route_len)
        best_candidate = neighbors[0]
        best_candidate_route, best_candidate_route_len, _ = solution_to_route(best_candidate, data)
        best_candidate_distance = fitness_func(data, best_candidate_route)
        best_candidate_ix = 0
        for neighbor_ix, neighbor in enumerate(neighbors):
            neighbor_route, neighbor_route_len, _ = solution_to_route(neighbor, data)
            neighbor_distance = fitness_func(data, neighbor_route)
            if neighbor_distance < best_candidate_distance and not is_in_tabu(neighbor_route, tabu_list):
                best_candidate = neighbor
                best_candidate_ix = neighbor_ix
                best_candidate_route, best_candidate_route_len = neighbor_route, neighbor_route_len
                best_candidate_distance = neighbor_distance
        if best_candidate_distance < best_distance:
            best_sol = best_candidate
            best_distance = best_candidate_distance
        print("Iteration {0}: {1} (Best Candidate Distance: {2} [Operator {3}])".format(iteration, best_distance,
                                                                                        best_candidate_distance,
                                                                                        best_candidate_ix % 5 + 1))
        tabu_list.append(best_candidate_route)
        if len(tabu_list) > max_tabu_size:
            tabu_list.pop(0)
    best_route, _, final_data = solution_to_route(best_sol, data, is_final=True)
    return best_route, best_distance, final_data
