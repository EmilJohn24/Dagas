import os

# Create your tests here.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DagasServer.settings')
import django

django.setup()
from relief.models import DonorProfile
from relief.tasks import solo_algo_tests, generate_data
print("Generating dataset...")
# generate_data(donor_count=1, evacuation_center_count=70,
#               min_demand=10, max_demand=30,
#               min_supply=150, max_supply=200)
print("Done generating dataset...")
# donor_id = DonorProfile.objects.all()[0].pk
donor_id = DonorProfile.objects.get(user__username="FakeDonor0").id
solo_algo_tests("tabu", donor_id, None)
