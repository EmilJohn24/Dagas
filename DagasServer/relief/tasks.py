import copy
import sys
from itertools import islice

from celery import shared_task

# app = Celery('tasks', broker='pyamqp://guest@localhost//')
# https://docs.celeryq.dev/en/stable/getting-started/next-steps.html#next-steps
# https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html#first-steps
# https://docs.celeryq.dev/en/latest/django/first-steps-with-django.html#using-celery-with-django
from relief.models import DonorProfile, BarangayRequest, User, ItemType, Supply

# Algorithm section
# Algorithm-related imports
from sklearn.neighbors import BallTree
import numpy as np
import pandas as pd
from haversine import haversine_vector, Unit


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


# def donor_request_count(donor_index, algo_data, data):
#     count = 0
#     request_list
#     for item_type in data['item_types']:
#         assignments = algo_data['request_assignments_' + item_type]
#         count += assignments.count(donor_index)
#     return count
# def is_donor_assigned_to_request(donor_index, request_index, algo_data, data):
#     for item_type in data['item_types']:
#         if algo_data['request_assignments_' + item_type][request_index] == donor_index:
#             return True
#     return False

def algo_v1(orig_data):
    # Algo-data setup
    #   1: Requests assigned to each donor
    data = copy.deepcopy(orig_data)  # copy the contents of the data model

    algo_data = {}
    algo_data['donor_request_counts'] = [0] * data['num_vehicles']
    algo_data['routes'] = []
    for i in range(data['num_vehicles']):
        algo_data['routes'].append([])
    algo_data['min_add_distance'] = [sys.maxsize] * data['num_requests']
    algo_data['request_assignments'] = [None] * data['num_requests']

    def distance_n2n(src_node, dst_node):
        return data['distance_matrix'][src_node][dst_node]

    def distance_delta_n2n(src_node, new_node, dst_node):
        return distance_n2n(src_node, new_node) + distance_n2n(new_node, dst_node) \
               - distance_n2n(src_node, dst_node)

    def cheapest_insertion(route, src_donor_index, new_node):
        """ Donor to first node"""

        first_distance = distance_n2n(data['starts'][src_donor_index], new_node)
        if len(route) == 1:
            return 1, first_distance
        distances = [distance_delta_n2n(head, new_node, tail) for (head, tail) in window(route, 2)]

        min_distance = min(distances)
        return distances.index(min_distance) + 1, min_distance

    for item_type in data['item_types']:
        algo_data['request_assignments_' + item_type] = [None] * data['num_requests']
    item_type_index = 0
    for i in range(data['num_requests']):
        # Loop through unassigned requests
        chosen_donor_index = None
        chosen_request_index = None
        chosen_position = None
        for request_index in [index for index, x in enumerate(algo_data['request_assignments']) if x is None]:

            for donor_index in range(data['num_vehicles']):
                donor_supply = data[data['supply_types'][item_type_index]][donor_index]
                request_demand = data[data['demand_types'][item_type_index]][request_index]
                if donor_supply >= request_demand:
                    if algo_data['donor_request_counts'][donor_index] == 0:
                        distance = distance_n2n(data['starts'][donor_index], request_index)
                        if distance < algo_data['min_add_distance'][i]:
                            algo_data['min_add_distance'][i] = distance
                            chosen_donor_index = donor_index
                            chosen_request_index = request_index
                            chosen_position = 0
                    else:
                        index, distance = cheapest_insertion(algo_data["routes"][donor_index], donor_index,
                                                             request_index)
                        if distance < algo_data['min_add_distance'][i]:
                            algo_data['min_add_distance'][i] = distance
                            chosen_donor_index = donor_index
                            chosen_request_index = request_index
                            chosen_position = index
        # insertion here (including all updates)
        if chosen_position is not None:
            algo_data["routes"][chosen_donor_index].insert(chosen_position, chosen_request_index)
        else:
            algo_data["routes"][chosen_donor_index].insert(0, chosen_request_index)
        algo_data['donor_request_counts'][chosen_donor_index] += 1
        supply_reduced = data[data['demand_types'][item_type_index]][chosen_request_index]
        algo_data['request_assignments'][chosen_request_index] = chosen_donor_index
        data[data['supply_types'][item_type_index]][chosen_donor_index] -= supply_reduced
        data[data['demand_types'][item_type_index]][chosen_request_index] = 0
    manipulated_data = data
    return algo_data, manipulated_data


def generate_data_model_from_db():
    """
    Returns a dictionary containing all relevant data sets from the database
    """
    data = {}
    # Distance Matrix (Heaviside in meters)
    #   Phase 1: Get Evacuation Latitudes and Longitudes
    evacuation_geolocations = list(BarangayRequest.objects.values_list('evacuation_center__geolocation', flat=True))
    evacuation_lats = list(map(lambda request_tuple: request_tuple.lat, evacuation_geolocations))
    evacuation_lons = list(map(lambda request_tuple: request_tuple.lon, evacuation_geolocations))

    #   Phase 2: Get Donor Latitudes and Longitudes
    donors = DonorProfile.objects.all()

    valid_donor = []
    donor_lats = []
    donor_lons = []
    for donor in donors:
        # TODO: Consider creating geolocation for user directly.
        if donor.user.get_most_recent_location():
            donor_lats.append(donor.user.get_most_recent_location().geolocation.lat)
            donor_lons.append(donor.user.get_most_recent_location().geolocation.lon)
            valid_donor.append(donor)
    #   Phase 3: Append coordinates (for haversine)
    combined_coords = list(zip(evacuation_lats + donor_lats, evacuation_lons + donor_lons))
    combined_coords_len = len(combined_coords)
    data['distance_matrix'] = haversine_vector(combined_coords, combined_coords, Unit.METERS, comb=True)

    # Vehicle Count (Donor count) and Request Count
    data['num_vehicles'] = len(valid_donor)
    data['num_requests'] = len(evacuation_geolocations)
    # Start and end points (donor)
    data['starts'] = list(range(combined_coords_len - data['num_vehicles'], combined_coords_len))
    data['ends'] = data['starts']

    # Demand and supply load
    barangay_requests = BarangayRequest.objects.all()
    data['item_types'] = []
    data['demand_types'] = []
    data['supply_types'] = []
    for item_type in ItemType.objects.all():
        item_type_name = item_type.name
        demand_type_name = item_type_name + '_demand'
        supply_type_name = item_type_name + '_supply'
        data['item_types'].append(item_type_name)
        data['demand_types'].append(demand_type_name)
        data['supply_types'].append(supply_type_name)
        data[demand_type_name] = []
        data[supply_type_name] = []
        for request in barangay_requests:
            data[demand_type_name].append(request.calculate_untransacted_pax(item_type))
        for donor in valid_donor:
            total_supply = 0
            supplies = Supply.objects.filter(donation__donor=donor, type=item_type)
            for supply in supplies:
                total_supply += supply.calculate_available_pax()
            data[supply_type_name].append(total_supply)

    return data


# https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.BallTree.html
def nearest_neighbor_query(lats, lons, tree, requests, k=5, ):
    distances, indices = tree.query(np.deg2rad(np.c_[lats, lons]), k=k)
    # nearest_evacs = requests['name'].iloc[indices[:, 0]]

    return distances, indices


def generate_tree(evacuation_centers, geolocations):
    barangay_requests = BarangayRequest.objects.all()

    geolocation_lats = list(map(lambda request_tuple: request_tuple.lat, geolocations))
    geolocation_lons = list(map(lambda request_tuple: request_tuple.lon, geolocations))

    requests = pd.DataFrame(data={
        'name': evacuation_centers,
        'lat': geolocation_lats,
        'lon': geolocation_lons,
    })
    return BallTree(np.deg2rad(requests[['lat', 'lon']].values), metric='haversine'), requests
    # lng = []
    # for barangay_request in barangay_requests:
    #     lat.append(barangay_request.evacuation_center.)


@shared_task
def algorithm():
    data = generate_data_model_from_db()
    # print(data['distance_matrix'])
    results, manipulated_data = algo_v1(data)
    # donors = DonorProfile.objects.all()
    # barangay_requests = BarangayRequest.objects.all()
    # evacuation_centers = BarangayRequest.objects.values_list('evacuation_center', flat=True)
    # geolocations = list(BarangayRequest.objects.values_list('evacuation_center__geolocation', flat=True))
    # tree, requests = generate_tree(evacuation_centers=evacuation_centers, geolocations=geolocations)

    # query_valid = []
    # query_lat = []
    # query_lon = []
    # for donor in donors:
    #     # TODO: Consider creating geolocation for user directly.
    #     if donor.user.get_most_recent_location():
    #         query_lat.append(donor.user.get_most_recent_location().geolocation.lat)
    #         query_lon.append(donor.user.get_most_recent_location().geolocation.lon)
    #         query_valid.append(donor)

    # _, indices = nearest_neighbor_query(query_lat, query_lon, tree, requests)
    # print(indices)
    return
