# TODO: Create user groups
#   See https://stackoverflow.com/questions/4789021/in-django-how-do-i-check-if-a-user-is-in-a-certain-group
from django.contrib.auth.models import Group

# Groups
victims, victims_created = Group.objects.get_or_create(name='victims')
barangays, barangays_created = Group.objects.get_or_create(name='barangays')
donors, donors_created = Group.objects.get_or_create(name='donors')
# Permissions
# TODO: Create permissions based on future Models
# Permission to Group Assignments
