import copy
import sys

import numpy as np


def distance_between(a, b, data):
    return data['distance_matrix'][a][b]


def lnnh(data, n_neighbors):
    working_data = copy.deepcopy(data)
    working_data['fulfillment_matrix'] = np.zeros((working_data['num_requests'],
                                                   len(working_data['item_types'])))

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

    def update_demand(req_ix):
        """Update current supply and demand based on chosen pair"""
        for type_index in range(len(working_data['item_types'])):
            current_supply = working_data['supply_matrix'][type_index]
            current_demand = working_data['demand_matrix'][req_ix][type_index]
            surplus = current_supply - current_demand
            working_data['fulfillment_matrix'][req_ix, type_index] += abs(surplus)
            if surplus >= 0:
                working_data['demand_matrix'][req_ix][type_index] = 0
                working_data['supply_matrix'][type_index] = surplus

            else:
                working_data['demand_matrix'][req_ix][type_index] = abs(surplus)
                working_data['supply_matrix'][type_index] = 0

    donor_request_counts = np.zeros(data['num_vehicles'])
    request_count = data['num_requests']
    # gene = Donor
    route = []
    donor_matrix_ix = request_count
    current_node = donor_matrix_ix
    # if np.sum(working_data['demand_matrix']) == 0:
    #     break
    while not np.sum(working_data['supply_matrix']) == 0:
        closest_requests = np.argsort(data['distance_matrix'][current_node, :request_count])
        closest_requests = closest_requests[closest_requests != current_node]
        a = np.isin(closest_requests, route)
        closest_requests = closest_requests[np.logical_not(np.isin(closest_requests, route))]
        unfinished_requests = np.where(np.sum(working_data['demand_matrix'][closest_requests], axis=1) != 0)
        unfinished_closest_requests = closest_requests[unfinished_requests]
        cheapest_distance = sys.maxsize
        cheapest_neighbors = None
        neighbor_layer_1 = unfinished_closest_requests[:n_neighbors]
        for neighbor_ix in neighbor_layer_1:
            resulting_supply = check_resulting_supply(working_data['supply_matrix'], neighbor_ix)
            if np.sum(resulting_supply) == 0:
                if distance_between(current_node, neighbor_ix, data) < cheapest_distance:
                    cheapest_distance = distance_between(current_node, neighbor_ix, data)
                    cheapest_neighbors = [neighbor_ix]
                continue
            neighbor_closest_requests = np.argsort(data['distance_matrix'][neighbor_ix,
                                                   :request_count])
            neighbor_closest_requests = neighbor_closest_requests[np.logical_and(
                neighbor_closest_requests != current_node,
                neighbor_closest_requests != neighbor_ix)]
            # np.logical_not(np.isin(closest_requests, routes[gene]))
            neighbor_closest_requests = neighbor_closest_requests[np.logical_not(
                np.isin(neighbor_closest_requests, route))]
            unfinished_neighbor_requests = np.where(np.sum(
                data['demand_matrix'][neighbor_closest_requests], axis=1) != 0)
            unfinished_closest_neighbor_requests = neighbor_closest_requests[unfinished_neighbor_requests]
            neighbor_layer_2 = unfinished_closest_neighbor_requests[:n_neighbors]
            for neighbor_ix_2 in neighbor_layer_2:
                distance = distance_between(current_node, neighbor_ix, data) + distance_between(neighbor_ix,
                                                                                                neighbor_ix_2, data)
                if distance < cheapest_distance:
                    cheapest_distance = distance
                    cheapest_neighbors = [neighbor_ix, neighbor_ix_2]
        for cheap_neighbor in cheapest_neighbors:
            route.append(cheap_neighbor)
            update_demand(cheap_neighbor)
    return route, working_data
