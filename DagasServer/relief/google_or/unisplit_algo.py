import copy

import numpy as np
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


def get_routes(solution, routing, manager, real_node_mapping, has_head=True):
    """Get vehicle routes from a solution and store them in an array."""
    # Get vehicle routes and store them in a two dimensional array whose
    # i,j entry is the jth location visited by vehicle i along its route.
    routes = []
    for route_nbr in range(routing.vehicles()):
        index = routing.Start(route_nbr)
        route = []
        if has_head:
            route = [manager.IndexToNode(index)]
        while not routing.IsEnd(index):
            index = solution.Value(routing.NextVar(index))
            if index in real_node_mapping.keys():
                actual_node_index = real_node_mapping[index]['request_ix']
                route.append(actual_node_index)
            else:
                route.append(manager.IndexToNode(index))
        route = np.array(route)
        counts, indexes = np.unique(route, return_index=True)
        routes.append(route[np.sort(indexes)])
        # routes.append([route[ix] for ix in sorted(indexes)])
    return routes


def print_or_solution(data, manager, routing, solution, real_node_mapping):
    print(f'Objective: {solution.ObjectiveValue()}')
    total_distance = 0
    total_loads = [0] * len(data['demand_types'])
    data_copy = copy.deepcopy(data)
    routes = get_routes(solution, routing, manager, real_node_mapping, has_head=False)
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)

        # plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        route_loads = [0] * len(data['demand_types'])
        routing_end = routing.End(vehicle_id)
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            # plan_output += ' {0} Load('.format(node_index)
            if node_index not in data['starts']:
                for i in range(len(data['demand_types'])):
                    # plan_output += str(data['demand_matrix'][node_index, i]) + ','
                    if real_node_mapping[node_index]['type_ix'] == i:
                        route_loads[i] += 1
            # plan_output += ') ->'

            previous_index = index
            index = solution.Value(routing.NextVar(index))
            arc_cost = routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)

        # plan_output += 'Cumulative: {0} Load('.format(manager.IndexToNode(index))
        # for i in range(len(data['demand_types'])):
        #     plan_output += str(route_loads[i]) + ','
        # plan_output += ') \n'
        # plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        # plan_output += 'Load of the route: {}\n'.format(route_loads)
        # print(plan_output)
        total_distance += route_distance
        # if zip(total_loads, route_loads) is not None:
        total_loads = [a + b for a, b in zip(total_loads, route_loads)]
    print('Total distance of all routes: {}m'.format(total_distance))
    print('Total load of all routes: {}'.format(total_loads))


def unisplit_algo_or(data):
    """Solve the problem using Google OR"""
    # Step 1: Initial routes
    aaa = len(data['distance_matrix'])
    original_len = len(data['distance_matrix'])
    node_count = int(np.sum(data['demand_matrix']) + data['num_vehicles'])
    manager = pywrapcp.RoutingIndexManager(node_count,  # +1 for the pseudo-node
                                           data['num_vehicles'],
                                           data['starts'],
                                           data['ends'], )  # from data['ends'])
    routing = pywrapcp.RoutingModel(manager)

    # Generate mapping
    real_node_mapping = {}
    current_point = 0
    for request_ix in range(data['num_requests']):
        for type_ix in range(len(data['item_types'])):
            for i in range(int(data['demand_matrix'][request_ix, type_ix])):
                if current_point == data['num_requests']:
                    current_point = original_len
                real_node_mapping[current_point] = {'request_ix': request_ix,
                                                    'type_ix': type_ix}
                current_point = current_point + 1

    # Distance callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        if from_node >= original_len:
            from_node = real_node_mapping[from_node]['request_ix']
        if to_node >= original_len:
            to_node = real_node_mapping[to_node]['request_ix']
        return int(data['distance_matrix'][from_node][to_node])

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Constraints:
    # 1: Distance

    # 2: Demands
    def demand_callback_with_index(type_index):
        def demand_callback(from_index):
            local_type_index = type_index
            from_node = manager.IndexToNode(from_index)
            # print("New: " + str(from_node))
            # print(local_type_index)
            if from_node in data['starts']:
                return 0

            #
            if real_node_mapping[from_index]['type_ix'] == type_index:
                return 1
            else:
                return 0
            # # print(demand_data)
            # demand = data['demand_matrix'][from_node, type_index]

        return demand_callback

    # i = 0
    # demand_callback_index = routing.RegisterUnaryTransitCallback(
    #     demand_callback_with_index(i)
    # )
    # routing.AddDimensionWithVehicleCapacity(
    #     demand_callback_index,
    #     0,
    #     data['supply_matrix'][:, i],
    #     True,
    #     data['item_types'][i],
    # )

    for i in range(len(data['item_types'])):
        demand_callback_index = routing.RegisterUnaryTransitCallback(
            demand_callback_with_index(i))
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,
            # list(data['supply_matrix'][:, i]),
            [int(data['supply_matrix'][i])],
            True,
            data['item_types'][i],
        )
    # Allow dropping
    max_distance = np.max(data['distance_matrix'])
    for fake_node in real_node_mapping.keys():
        # routing.AddDisjunction([manager.IndexToNode(node)], 1)
        routing.AddDisjunction([manager.IndexToNode(fake_node)], 2*int(max_distance))
    # Perform algorithm
    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.TABU_SEARCH)
    search_parameters.time_limit.FromSeconds(120)
    # search_parameters.solution_limit = 5
    # Solve the problem.
    print("Finished initialization. Solving problem...")
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    print("Finished solving... Preparing results...")
    if solution is not None:
        print_or_solution(data, manager, routing, solution, real_node_mapping)
    return solution
