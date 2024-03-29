import copy
import sys
import warnings
from datetime import timedelta
from itertools import islice
import random

from mpl_toolkits.basemap import Basemap
from celery import shared_task

# app = Celery('tasks', broker='pyamqp://guest@localhost//')
# https://docs.celeryq.dev/en/stable/getting-started/next-steps.html#next-steps
# https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html#first-steps
# https://docs.celeryq.dev/en/latest/django/first-steps-with-django.html#using-celery-with-django
from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.db import SessionStore
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.utils.datetime_safe import datetime
from django.utils import timezone
from matplotlib import pyplot as plt
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from rest_framework import status

from relief.cplex.algorithm import cplex_algo
from relief.ga.algorithm import run_ga_algo, run_solo_ga_algo
from relief.google_or.tsp import algo_or
from relief.google_or.unisplit_algo import unisplit_algo_or
from relief.lnnh.algorithm import lnnh
from relief.models import DonorProfile, BarangayRequest, User, ItemType, Supply, ResidentProfile, Donation, \
    UserLocation, ItemRequest, Transaction, TransactionOrder, EvacuationCenter, BarangayProfile, Fulfillment, RouteNode, \
    RouteSuggestion, AlgorithmExecution

# Algorithm section
# Algorithm-related imports
import numpy as np
import pandas as pd
from haversine import haversine_vector, Unit

# Algorithm-related stuff
from relief.serializers import UserSerializer, EvacuationCenterSerializer, UserLocationSerializer, DonationSerializer, \
    CustomRegisterSerializer
from shapely.geometry import Polygon, Point

from relief.tabu.algorithm import tabu_algorithm, fitness_func


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


def print_or_solution(data, manager, routing, solution):
    print(f'Objective: {solution.ObjectiveValue()}')
    total_distance = 0
    total_loads = [0] * len(data['demand_types'])
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        # plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        route_loads = [0] * len(data['demand_types'])
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            # plan_output += ' {0} Load('.format(node_index)
            if node_index not in data['starts']:
                for i in range(len(data['demand_types'])):
                    # plan_output += str(data[data['demand_types'][i]][node_index]) + ','
                    route_loads[i] += data[data['demand_types'][i]][node_index]
            # plan_output += ') ->'

            previous_index = index
            index = solution.Value(routing.NextVar(index))
            # Ignore return trip
            if index == routing.End(vehicle_id):
                break
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        # plan_output += 'Cumulative: {0} Load('.format(manager.IndexToNode(index))
        # for i in range(len(data['demand_types'])):
        #     plan_output += str(route_loads[i]) + ','
        # plan_output += ') \n'
        # plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        # # plan_output += 'Load of the route: {}\n'.format(route_load)
        # print(plan_output)
        total_distance += route_distance
        total_loads = [a + b for a, b in zip(total_loads, route_loads)]
    print('Total distance of all routes: {}km'.format(total_distance / 1000))
    print('Total load of all routes: {}'.format(total_loads))


# Routing without constraints
def simple_detail_routing(data, donor_mat_index, route):
    # Step 0: If there are less than 2 nodes, there is no need for detail routing, so return the same route
    if len(route) <= 1:
        return route
    # Step 1: Initialize model
    donor_node = len(route)
    end_node_index = len(route) + 1
    manager = pywrapcp.RoutingIndexManager(len(route) + 2,  # route nodes + donor init node (1) + pseudo-node (1)
                                           1,  # number of vehicles
                                           [donor_node, ],
                                           [end_node_index, ], )  # starting point for donor
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        """This custom callback removes the need for making a sub-matrix of the distance matrix"""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        if from_node == end_node_index or to_node == end_node_index:
            return 0
        if from_node == donor_node:
            from_node = donor_mat_index
        else:
            from_node = route[from_node]

        if to_node == donor_node:
            to_node = donor_mat_index
        else:
            to_node = route[to_node]
        return int(data['distance_matrix'][from_node][to_node])

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.TABU_SEARCH)
    search_parameters.time_limit.FromSeconds(1)
    solution = routing.SolveWithParameters(search_parameters)

    # Convert solution back to large matrix indices
    new_route = []
    index = routing.Start(0)
    while not routing.IsEnd(index):
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        index_node = manager.IndexToNode(index)
        if index == routing.End(0):
            break
        new_route.append(route[index])
    return new_route


def algo_v1(orig_data, algo_data_init=None):
    # Algo-data setup
    #   1: Requests assigned to each donor
    data = copy.deepcopy(orig_data)  # copy the contents of the data model
    algo_data = None
    if algo_data_init is None:
        algo_data = {}
        algo_data['donor_request_counts'] = [0] * data['num_vehicles']
        algo_data['routes'] = []
        for i in range(data['num_vehicles']):
            algo_data['routes'].append([])
        algo_data['min_add_distance'] = [sys.maxsize] * data['num_requests']
        algo_data['request_assignments'] = [None] * data['num_requests']
        algo_data['fulfillment_matrix'] = np.zeros((data['num_vehicles'],
                                                    data['num_requests'], len(data['item_types'])))
    else:
        algo_data = copy.deepcopy(algo_data_init)
        # Copy over everything except request assignments
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

    # for item_type in data['item_types']:
    #     algo_data['request_assignments_' + item_type] = [None] * data['num_requests']
    for i in range(data['num_requests']):
        # Loop through unassigned requests
        chosen_donor_index = None
        chosen_request_index = None
        chosen_position = None
        for request_index in range(data['num_requests']):
            # for request_index in [index for index, x in enumerate(algo_data['request_assignments']) if x is None]:
            for donor_index in range(data['num_vehicles']):
                # donor_supply = data['supply_matrix'][donor_index][item_type_index]
                # request_demand = data['demand_matrix'][request_index][item_type_index]
                # if donor_supply >= request_demand > 0 and donor_supply > 0:
                if np.sum(data['supply_matrix'][donor_index]) > 0:
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
                        if distance < algo_data['min_add_distance'][i] \
                                and request_index not in algo_data["routes"][donor_index]:
                            algo_data['min_add_distance'][i] = distance
                            chosen_donor_index = donor_index
                            chosen_request_index = request_index
                            chosen_position = index
        # insertion here (including all updates)
        if chosen_donor_index is None:
            continue

        if chosen_position is not None:
            algo_data["routes"][chosen_donor_index].insert(chosen_position, chosen_request_index)
        else:
            algo_data["routes"][chosen_donor_index].insert(0, chosen_request_index)
        algo_data['donor_request_counts'][chosen_donor_index] += 1
        for type_index in range(len(data['item_types'])):
            current_supply = data['supply_matrix'][chosen_donor_index][type_index]
            current_demand = data['demand_matrix'][chosen_request_index][type_index]
            surplus = current_supply - current_demand
            algo_data['fulfillment_matrix'][chosen_donor_index, chosen_request_index, type_index] += abs(surplus)
            if surplus >= 0:
                data['demand_matrix'][chosen_request_index][type_index] = 0
                data['supply_matrix'][chosen_donor_index][type_index] = surplus

            else:
                data['demand_matrix'][chosen_request_index][type_index] = abs(surplus)
                data['supply_matrix'][chosen_donor_index][type_index] = 0
        donor_mat_index = data['starts'][chosen_donor_index]
        algo_route = algo_data['routes'][chosen_donor_index]
        algo_data['routes'][chosen_donor_index] = simple_detail_routing(data, donor_mat_index, algo_route)
    # for i in range(len(algo_data['routes'])):
    #     donor_mat_index = data['starts'][i]
    #     algo_data['routes'][i] = simple_detail_routing(data, donor_mat_index, algo_data['routes'][i])

    manipulated_data = data
    return algo_data, manipulated_data


def algo_main(data):
    current_data = data
    algo_data = None
    for i in range(len(data['item_types'])):
        algo_data, current_data = algo_v1(current_data, item_type_index=i, algo_data_init=algo_data)
    return algo_data, current_data


# Data handling
def generate_data_model_from_db(solo_mode=False, solo_donor=None):
    """
    Returns a dictionary containing all relevant data sets from the database
    """
    data = {}
    # Distance Matrix (Heaviside in meters)
    #   Phase 1: Get Evacuation Latitudes and Longitudes
    barangay_request_ids = [barangay_request.id for barangay_request in BarangayRequest.objects.all() if
                            not barangay_request.is_handled()]
    barangay_requests = BarangayRequest.objects.filter(id__in=barangay_request_ids)
    evacuation_geolocations = list(barangay_requests.values_list('evacuation_center__geolocation', flat=True))
    evacuation_lats = list(map(lambda request_tuple: request_tuple.lat, evacuation_geolocations))
    evacuation_lons = list(map(lambda request_tuple: request_tuple.lon, evacuation_geolocations))

    # plt.show()
    #   Phase 2: Get Donor Latitudes and Longitudes
    donors = None
    valid_donors = []
    donor_lats = []
    donor_lons = []
    if not solo_mode:
        donors = DonorProfile.objects.all()

        for donor in donors:
            # TODO: Consider creating geolocation for user directly.
            if donor.user.get_most_recent_location():
                donor_lats.append(donor.user.get_most_recent_location().geolocation.lat)
                donor_lons.append(donor.user.get_most_recent_location().geolocation.lon)
                valid_donors.append(donor)
    else:
        if solo_donor.user.get_most_recent_location():
            donor_lats.append(solo_donor.user.get_most_recent_location().geolocation.lat)
            donor_lons.append(solo_donor.user.get_most_recent_location().geolocation.lon)
            valid_donors.append(solo_donor)

        else:
            raise ValidationError("Your location is unknown", code=status.HTTP_400_BAD_REQUEST, )
    # Map Plotting
    # Testing only:
    # Philippine Bounding Box: 117,5,127,19)),
    # EPSG: https://spatialreference.org/ref/epsg/?search=Philippines&srtext=Search
    # https://matplotlib.org/basemap/api/basemap_api.html#mpl_toolkits.basemap.Basemap.arcgisimage
    # Manila: Box 120.693515,14.437993,121.318281,14.875347
    ph_map = Basemap(resolution=None,
                     projection='lcc',
                     # lat_0=11.9, lon_0=122.5,
                     epsg='3121',
                     llcrnrlon=120.693515, llcrnrlat=14.437993, urcrnrlon=121.318281, urcrnrlat=14.875347)
    # ph_map.drawcoastlines()
    # ph_map.drawmapboundary(zorder=0)
    # ph_map.fillcontinents(color='#ffffff', zorder=1)
    # ph_map.drawcountries(linewidth=1.5)
    # ph_map.drawstates()
    # ph_map.drawcounties(color='darkred')
    ph_map.arcgisimage(verbose=True)

    for evac_lat, evac_lon in zip(evacuation_lats, evacuation_lons):
        evac_x, evac_y = ph_map(evac_lon, evac_lat)
        ph_map.plot(evac_x, evac_y, 'r^', markersize=2)
    donor_x, donor_y = ph_map(donor_lons[0], donor_lats[0])
    ph_map.plot(donor_x, donor_y, 'b^', markersize=2)
    data['map'] = ph_map
    data['evac_lats'] = evacuation_lats
    data['evac_lons'] = evacuation_lons
    data['donor_lat'] = donor_lats
    data['donor_lon'] = donor_lons

    # End map

    #   Phase 3: Append coordinates (for haversine)
    combined_coords = list(zip(evacuation_lats + donor_lats, evacuation_lons + donor_lons))
    combined_coords_len = len(combined_coords)
    data['distance_matrix'] = haversine_vector(combined_coords, combined_coords, Unit.METERS, comb=True)

    # Vehicle Count (Donor count) and Request Count
    data['num_vehicles'] = len(valid_donors)
    data['num_requests'] = len(evacuation_geolocations)
    # Start and end points (donor)
    data['starts'] = list(range(combined_coords_len - data['num_vehicles'], combined_coords_len))
    data['ends'] = data['starts']

    # Demand and supply load

    data['item_types'] = []
    data['demand_types'] = []
    data['supply_types'] = []
    data['demand_matrix'] = np.zeros((len(barangay_requests), len(ItemType.objects.all())))
    if solo_mode:
        data['supply_matrix'] = np.zeros(len(ItemType.objects.all()))
    else:
        data['supply_matrix'] = np.zeros((len(valid_donors), len(ItemType.objects.all())))
    for type_index, item_type in enumerate(ItemType.objects.all()):
        item_type_name = item_type.name
        demand_type_name = item_type_name + '_demand'
        supply_type_name = item_type_name + '_supply'
        data['item_types'].append(item_type_name)
        data['demand_types'].append(demand_type_name)
        data['supply_types'].append(supply_type_name)
        data[demand_type_name] = []
        data[supply_type_name] = []
        for request_index, request in enumerate(barangay_requests):
            data['demand_matrix'][request_index][type_index] = request.calculate_untransacted_pax(item_type) \
                                                               - request.calculate_suggested_pax(item_type)
            data[demand_type_name].append(request.calculate_untransacted_pax(item_type))
        data[demand_type_name + '_total'] = sum(data[demand_type_name])
        if not solo_mode:
            for donor_ix, donor in enumerate(valid_donors):
                total_supply = 0
                supplies = Supply.objects.filter(donation__donor=donor, type=item_type)
                for supply in supplies:
                    total_supply += supply.calculate_available_pax()
                data[supply_type_name].append(total_supply)
                data['supply_matrix'][donor_ix][type_index] = total_supply
        else:
            total_supply = 0
            supplies = Supply.objects.filter(donation__donor=solo_donor, type=item_type) | Supply.objects.filter(
                donor=solo_donor, type=item_type)
            for supply in supplies:
                total_supply += supply.calculate_available_pax()
            data[supply_type_name].append(total_supply)
            data['supply_matrix'][type_index] = total_supply
    data['donor_objs'] = valid_donors
    data['request_objs'] = list(barangay_requests)
    return data


@shared_task
def generate_data(donor_count=10, evacuation_center_count=10,
                  min_demand=100, max_demand=1000, barangay_names=None,
                  min_supply=1000, max_supply=10000):
    # Clear dataset
    random.seed(1)
    warnings.filterwarnings('ignore', 'DateTimeField*')

    def polygon_random_points(poly, num_points):
        min_x, min_y, max_x, max_y = poly.bounds
        points = []
        while len(points) < num_points:
            random_point = Point([random.uniform(min_x, max_x), random.uniform(min_y, max_y)])
            if random_point.within(poly):
                points.append(random_point)
        return points

    # A random polygon around Luzon that dictates the range of generated evacuation centers
    # generation_polygon = Polygon([(14.798263, 120.921852), (14.873512, 121.074507),
    #                               (14.553057, 121.164575), (14.516944, 121.004209)])
    # Pateros Bounding Box
    generation_polygon = Polygon([(14.552783, 121.064408), (14.550782, 121.078887),
                                  (14.535703, 121.070605), (14.545624, 121.059724)])
    # Step 1: Generate users
    #   Step 1a: Clear all donors, supplies, and donations
    User.objects.filter(role=User.DONOR).delete()
    User.objects.filter(role=User.BARANGAY).delete()
    UserLocation.objects.all().delete()
    DonorProfile.objects.all().delete()
    Donation.objects.all().delete()
    Supply.objects.all().delete()
    BarangayRequest.objects.all().delete()
    EvacuationCenter.objects.all().delete()
    ItemRequest.objects.all().delete()
    Transaction.objects.all().delete()
    TransactionOrder.objects.all().delete()
    #   Step 1b: Create pseudo-barangay and evacuation centers
    if barangay_names is None:
        barangay_names = [f'Barangay_1']
    for barangay_name in barangay_names:
        if not User.objects.filter(role=User.BARANGAY, username=barangay_name):
            test_barangay = get_user_model().objects.create_user(
                username=barangay_name,
                password="barangay123",
                email=f'{barangay_name}@gmail.com',
                first_name="Barangay",
                last_name=barangay_name,
                role=User.BARANGAY,
            )
            test_barangay.save()
        # Step 1b-2: Generate evacuation centers
        barangay_user = User.objects.filter(role=User.BARANGAY, username=barangay_name)[0]
        barangay = BarangayProfile.objects.filter(user=barangay_user)[0]
        generated_points = polygon_random_points(generation_polygon, evacuation_center_count)
        for i, point in enumerate(generated_points):
            # Generate evacuation center
            point_str = str(point.x) + "," + str(point.y)
            random_evacuation = EvacuationCenter.objects.create(
                name="Evacuation" + str(i),
                barangays=barangay,
                address="N/A",
                geolocation=point_str,
            )
            if random_evacuation:
                # Step 2: Generate requests

                request = BarangayRequest.objects.create(
                    evacuation_center=random_evacuation,
                    expected_date=datetime.now(timezone.utc) + timedelta(days=1),
                    barangay=barangay,
                )
                # Generate item request for each type
                for item_type in ItemType.objects.all():
                    random_pax = random.randrange(min_demand, max_demand)
                    ItemRequest.objects.create(
                        barangay_request=request,
                        date_added=datetime.now(timezone.utc),
                        pax=random_pax,
                        type=item_type,
                    )

    #   Step 1c: Generate donors (with locations and donations)
    generated_donor_points = polygon_random_points(generation_polygon, donor_count)
    for i, point in enumerate(generated_donor_points):
        donor_point_str = str(point.x) + "," + str(point.y)
        donor_name = "Donor" + str(i)
        if not User.objects.filter(role=User.DONOR, username=donor_name):
            new_donor = get_user_model().objects.create_user(
                username=donor_name,
                password="donor123",
                email="donor" + str(i) + "@gmail.com",
                first_name="Generic",
                last_name="Donor",
                role=User.DONOR,
            )
        donor_user = User.objects.filter(role=User.DONOR, username=donor_name)[0]
        donor = DonorProfile.objects.filter(user=donor_user)[0]
        UserLocation.objects.create(
            user=donor_user,
            geolocation=donor_point_str,
            time=datetime.now(timezone.utc),
        )
        pseudo_donation = Donation.objects.create(
            donor=donor,
            datetime_added=datetime.now(timezone.utc),
        )

        # Generate supplies
        for item_type in ItemType.objects.all():
            random_quantity = random.randrange(min_supply, max_supply)
            new_supply = Supply.objects.create(
                name="GenericSupply",
                type=item_type,
                pax=random_quantity,
                quantity=random_quantity,
                donation=pseudo_donation,
            )


def randomize_dates(days_covered=10):
    def randomizer():
        return datetime.now(timezone.utc) - timedelta(days=random.randint(0, days_covered))

    for supply in Supply.objects.all():
        supply.datetime_added = randomizer()
        supply.save()
    for item_request in ItemRequest.objects.all():
        item_request.date_added = randomizer()
        item_request.save()
    for transaction in Transaction.objects.all():
        transaction.created_on = randomizer()


def generate_data_from_file(filename, **kwargs):
    barangay_names = open(filename).read().splitlines()
    kwargs['barangay_names'] = barangay_names
    return generate_data(**kwargs)


# Output
def routes_to_db(input_data, algo_data):
    # Fulfillment.objects.all().delete()
    # RouteSuggestion.objects.all().delete()
    # RouteNode.objects.all().delete()

    def distance_n2n(src_node, dst_node):
        return input_data['distance_matrix'][src_node][dst_node]

    donors = input_data['donor_objs']
    requests = input_data['request_objs']
    routes = algo_data['routes']
    fulfillments = algo_data['fulfillment_matrix']
    for donor_index, route in enumerate(routes):
        current_donor = donors[donor_index]
        current_route = routes[donor_index]
        suggestion = RouteSuggestion.objects.create(
            donor=current_donor,
        )
        for position, request_index in enumerate(current_route):
            request_object = requests[request_index]
            route_node = None
            if position == 0:
                distance_from_prev = distance_n2n(input_data['starts'][donor_index], request_index)
                route_node = RouteNode.objects.create(
                    request=request_object,
                    distance_from_prev=distance_from_prev,
                    suggestion=suggestion,
                )
            else:
                distance_from_prev = distance_n2n(current_route[position - 1], request_index)
                route_node = RouteNode.objects.create(
                    request=request_object,
                    distance_from_prev=distance_from_prev,
                    suggestion=suggestion,
                )

                # class Fulfillment(models.Model):
                #     """Single item fulfillment connected to routenode"""
                #     node = models.ForeignKey(to=RouteNode, on_delete=models.CASCADE, )
                #     type = models.ForeignKey(to=ItemType, on_delete=models.CASCADE, )
                #     pax = models.IntegerField()
            for item_type_index, item_count in enumerate(list(fulfillments[donor_index][request_index])):
                # Create new fulfillment
                item_type = ItemType.objects.all()[item_type_index]
                Fulfillment.objects.create(
                    node=route_node,
                    type=item_type,
                    pax=item_count,
                )


def result_to_db(donor, route, final_data):
    requests = final_data['request_objs']
    fulfillments = final_data['fulfillment_matrix']
    suggestion = RouteSuggestion.objects.create(
        donor=donor,
    )
    for position, request_index in enumerate(route):
        request_object = requests[request_index]
        route_node = None
        if position == 0:
            distance_from_prev = final_data['distance_matrix'][final_data['starts'][0]][request_index]
            route_node = RouteNode.objects.create(
                request=request_object,
                distance_from_prev=distance_from_prev,
                suggestion=suggestion,
            )
        else:
            distance_from_prev = final_data['distance_matrix'][route[position - 1]][route[position]]
            route_node = RouteNode.objects.create(
                request=request_object,
                distance_from_prev=distance_from_prev,
                suggestion=suggestion,
            )

        for item_type_index, item_count in enumerate(list(fulfillments[request_index])):
            # Create new fulfillment
            item_type = ItemType.objects.all()[item_type_index]
            Fulfillment.objects.create(
                node=route_node,
                type=item_type,
                pax=item_count,
            )
    return suggestion


@shared_task()
def algo_error_handler(request, exc, traceback, **kwargs):
    AlgorithmExecution.objects.get(id=kwargs['algo_exec_id']).delete()


@shared_task()
def solo_algo_tests(model, donor_ix, algo_exec_id):
    # donors = DonorProfile.objects.all()
    # donor = donors[random.randint(0, len(donors) - 1)]
    # donor = donors[donor_ix]
    algo_execution = None
    if algo_exec_id is not None:
        algo_execution = AlgorithmExecution.objects.get(id=algo_exec_id)
    try:
        donor = DonorProfile.objects.get(pk=donor_ix)
        print("Generating data model from database...")
        data = generate_data_model_from_db(solo_mode=True, solo_donor=donor)
        total_demands = np.sum(data['demand_matrix'], axis=0)
        excess = total_demands - np.sum(data['supply_matrix'], axis=0)
        print("Displaying maximum distributed supplies...")
        print(data['supply_matrix'])
        print("Displaying minimum/ideal fulfillment ratios...")
        print(np.divide(excess, total_demands))
        # print("Calculating custom algorithm...")
        # results, manipulated_data = algo_main(data)
        res = None
        # if model == "standard":
        #     print("Running the greedy simple algorithm")
        #     return algo_v1(data)
        # elif model == "google-or":
        #     print("Calculating using Google OR algorithm...")
        #     unisplit_algo_or(data)
        #     return
        route = None
        if model == "ga":
            print("Running the genetic algorithm model...")
            res, problem = run_solo_ga_algo(data)
            route, _ = problem.chromosome_to_routes(res.X[0])

        if model == "or":
            print("Running the Google OR algorithm...")
            or_res = algo_or(data)
        if model == "or-split":
            print("Running slow OR split algorithm...")
            or_res = unisplit_algo_or(data)
        if model == "cplex":
            print("Running the CPLEX algo for benchmarking...")
            cplex_algo(data)
        if model == "lnnh":
            print("Running the LNNH algorithm")
            route, working_data = lnnh(data, n_neighbors=5)
            distance = fitness_func(data, route)
            print("Distance covered: {}".format(distance))
        if model == "tabu":
            print("Running the Tabu search")
            route, _, final_data = tabu_algorithm(data)
            if algo_execution is not None:
                suggestion = result_to_db(donor, route, final_data)
                algo_execution.result = suggestion
                algo_execution.save()
        if route is not None:
            ph_map = data['map']
            donor_x, donor_y = ph_map(data['donor_lon'][0], data['donor_lat'][0])
            evacs_lats, evacs_lons = data['evac_lats'], data['evac_lons']
            x = [donor_x]
            y = [donor_y]

            # ph_map.drawgreatcircle(donor_y, donor_x, evacs_y[0], evacs_x[0], color='c', linewidth=3)
            for node in route:
                node_x, node_y = ph_map(evacs_lons[node], evacs_lats[node])
                x.append(node_x)
                y.append(node_y)
                # ph_map.drawgreatcircle(evacs_y[node_a], evacs_y[node_a], evacs_y[node_b], evacs_x[node_b])

            x.append(donor_x)
            y.append(donor_y)
            ph_map.plot(x, y, color='y', linewidth=1, zorder=0)
            plt.show()
    except Exception as exc:
        # Delete execution if it fails
        algo_execution.delete()
        raise exc


def algo_test(model):
    # print("Generating dataset...")
    # generate_data(donor_count=40, evacuation_center_count=40,
    #               min_demand=100, max_demand=1000,
    #               min_supply=100, max_supply=1000)
    print("Generating data model from database...")
    data = generate_data_model_from_db()
    total_demands = np.sum(data['demand_matrix'], axis=0)
    excess = total_demands - np.sum(data['supply_matrix'], axis=0)
    print("Displaying maximum distributed supplies...")
    print(data['supply_matrix'])
    print("Displaying minimum/ideal fulfillment ratios...")
    print(np.divide(excess, total_demands))
    # print("Calculating custom algorithm...")
    # results, manipulated_data = algo_main(data)
    res = None
    if model == "standard":
        print("Running the greedy simple algorithm")
        return algo_v1(data)
    elif model == "google-or":
        print("Calculating using Google OR algorithm...")
        unisplit_algo_or(data)
        return
    elif model == "ga":
        print("Running the genetic algorithm model...")
        return run_ga_algo(data)
    return res


@shared_task
def algorithm():
    data = generate_data_model_from_db()
    # print(data['distance_matrix'])
    results, manipulated_data = algo_main(data)
    # routes_to_db(data, results)
    return
