from celery import shared_task

# app = Celery('tasks', broker='pyamqp://guest@localhost//')
# https://docs.celeryq.dev/en/stable/getting-started/next-steps.html#next-steps
# https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html#first-steps
# https://docs.celeryq.dev/en/latest/django/first-steps-with-django.html#using-celery-with-django
from relief.models import DonorProfile, BarangayRequest, User

# Algorithm section
# Algorithm-related imports
from sklearn.neighbors import BallTree
import numpy as np
import pandas as pd


# https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.BallTree.html
def nearest_neighbor_query(lats, lons, tree, requests, k=5, ):
    distances, indices = tree.query(np.deg2rad(np.c_[lats, lons]), k=k)
    # nearest_evacs = requests['name'].iloc[indices[:, 0]]

    return distances, indices


def generate_tree():
    barangay_requests = BarangayRequest.objects.all()
    evacuation_centers = BarangayRequest.objects.values_list('evacuation_center', flat=True)
    geolocations = list(BarangayRequest.objects.values_list('evacuation_center__geolocation', flat=True))
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
    donors = DonorProfile.objects.all()
    barangay_requests = BarangayRequest.objects.all()
    tree, requests = generate_tree()
    query_valid = []
    query_lat = []
    query_lon = []
    for donor in donors:
        # TODO: Consider creating geolocation for user directly.
        if donor.user.get_most_recent_location():
            query_lat.append(donor.user.get_most_recent_location().geolocation.lat)
            query_lon.append(donor.user.get_most_recent_location().geolocation.lon)
            query_valid.append(donor)

    _, indices = nearest_neighbor_query(query_lat, query_lon, tree, requests)
    print(indices)
    return
