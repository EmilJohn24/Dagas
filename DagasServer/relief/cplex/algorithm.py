import numpy as np
from docplex.mp.model import Model


def distance_matrix_remap(matrix, i, j):
    if i == 0 and j != 0:
        return matrix[len(matrix) - 1][j - 1]
    if j == 0 and i != 0:
        return matrix[i - 1][len(matrix) - 1]
    else:
        return matrix[i - 1][j - 1]


def cplex_algo(data):
    rnd = np.random
    rnd.seed(0)
    request_ix = [i for i in range(data['num_requests'])]
    donor_ix = data['num_requests']
    node_ix = request_ix + [donor_ix]  # Add starting node
    arcs = [(i, j) for i in node_ix for j in node_ix if i != j]
    arc_distances = {(i, j): data['distance_matrix'][i][j] for i, j in arcs}

    mdl = Model('TSP')
    x = mdl.binary_var_dict(arcs, name='x')  # is arc used
    cum_demand_vars = []
    for name in data['item_types']:
        cum_demand_vars.append(mdl.continuous_var_dict(request_ix, name=name))
    # Objective:
    mdl.minimize(mdl.sum(arc_distances[i, j] * x[i, j] for i, j in arcs))
    # Constraints:
    # Constraint 1: Ensure every request node is visited at most once
    mdl.add_constraints(mdl.sum(x[i, j] for j in node_ix if j != i) <= 1 for i in request_ix)
    mdl.add_constraints(mdl.sum(x[i, j] for i in node_ix if j != i) <= 1 for j in request_ix)
    mdl.add_constraint(mdl.sum(x[donor_ix, j] for j in request_ix if j != donor_ix) == 1)
    mdl.add_constraint(mdl.sum(x[i, donor_ix] for i in request_ix if i != donor_ix) == 1)

    for j in request_ix:
        # Constraint 2: If a node is visited, it should also be left
        mdl.add_if_then(mdl.sum(x[j, i] for i in node_ix if j != i) == 1,
                        mdl.sum(x[i, j] for i in node_ix if j != i) == 1)
        # Constraint 3: If a node is not visited, it should not be left
        mdl.add_if_then(mdl.sum(x[j, i] for i in node_ix if j != i) == 0,
                        mdl.sum(x[i, j] for i in node_ix if j != i) == 0)

    for type_ix, cum_demand in enumerate(cum_demand_vars):
        actual_demands = data['demand_matrix'][:, type_ix]
        available_supply = data['supply_matrix'][type_ix]
        # mdl.add_constraint(mdl.sum(demand_var[i] for i in request_ix) >= available_supply)
        # Constraint 3: The cumulative demand should exceed or be equal to the available supply
        mdl.add_constraint(mdl.max(cum_demand) >= available_supply)
        # mdl.add_indicator_constraints(
        #     mdl.indicator_constraint(x[donor_ix, j], cum_demand[j] == actual_demands[j])
        #     for j in request_ix)
        # Constraint 4: The cumulative demand of j is equal to the cumulative demand of the previous node
        #               plus the demand for j
        mdl.add_indicator_constraints(
            mdl.indicator_constraint(x[i, j], cum_demand[i] + actual_demands[j] == cum_demand[j])
            for i, j in arcs if i != donor_ix and j != donor_ix)
        for j in request_ix:
            # Constraint 5: If a node is unvisited, its cumulative demand is 0
            mdl.add_if_then(mdl.sum(x[i, j] for i in node_ix if i != j) == 0, cum_demand[j] == 0)
            # Constraint 6: If the previous node of a visited node is the donor node, its cumulative demand
            #               is just its 
            mdl.add_if_then(x[donor_ix, j] == 1, cum_demand[j] == actual_demands[j])

    mdl.parameters.timelimit = 120
    solution = mdl.solve(log_output=True)
    print(solution)
    print(solution.solve_status)
