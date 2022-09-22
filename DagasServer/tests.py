import os

# Create your tests here.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DagasServer.settings')
import django

django.setup()
from relief.models import DonorProfile
from relief.tasks import solo_algo_tests, generate_data

# generate_data(donor_count=1, evacuation_center_count=20,
#               min_demand=10, max_demand=30,
#               min_supply=75, max_supply=100)
print("Done generating dataset...")
donor_id = DonorProfile.objects.all()[0].pk
solo_algo_tests("tabu", donor_id, None)
