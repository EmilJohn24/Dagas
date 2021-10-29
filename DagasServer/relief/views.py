from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
# For REST API-based views, use the list at: https://www.django-rest-framework.org/api-guide/generic-views/
from django.utils.decorators import method_decorator
from rest_framework import generics

from relief.decorators import role_required
from relief.models import User
from relief.serializers import UserSerializer

gov_admin_required = role_required(role_id=User.GOVERNMENT_ADMIN)


@method_decorator(login_required, name='dispatch')
@method_decorator(gov_admin_required, name='dispatch')
class UserListView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
