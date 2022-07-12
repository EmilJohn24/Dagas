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

    # Vehicle Count (Donor count)
    data['num_vehicles'] = len(valid_donor)
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
    print(data['distance_matrix'])
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
