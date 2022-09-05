import numpy as np
from pymoo.core.mutation import Mutation


class SwapMutation(Mutation):

    def _do(self, problem, X, **kwargs):
        for i in range(len(X)):
            r = np.random.random()

            # Swap two numbers (20% of the time)
            if r < 0.2:
                num_count = len(X[i])
                x1, x2 = np.random.randint(low=0, high=num_count, size=2)
                X[i][x1], X[i][x2] = X[i][x2], X[i][x1]

            # p = np.random.random()
            # Swap two numbers on the same donor
            # if p < 0.2:
            #     rem = X[i] // problem.algo_data['num_requests']
            #     donor_swap_index = np.random.randint(low=0, high=problem.algo_data['num_vehicles'])
            #     request_indices = np.where(rem == donor_swap_index)
            #     x1, x2 = np.random.choice(request_indices[0], size=2)
            #     X[i][x1], X[i][x2] = X[i][x2], X[i][x1]
        return X