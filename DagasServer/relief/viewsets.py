from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError

from relief.models import User, ResidentProfile
from relief.permissions import IsOwnerOrReadOnly, IsProfileUserOrReadOnly
from relief.serializers import UserSerializer, ResidentSerializer


# Guide: https://www.django-rest-framework.org/api-guide/viewsets/

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ResidentViewSet(viewsets.ModelViewSet):
    queryset = ResidentProfile.objects.all()
    serializer_class = ResidentSerializer

    # Can also be applied to views
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # def post(self, request, *args, **kwargs):
    #     file = request.data['file']
    #     profile = self.get_object()
    #     profile.gov_id = file
    #     profile.save()

    @action(detail=True, methods=['patch', 'put'], name='Upload ID', permission_classes=[IsProfileUserOrReadOnly])
    def upload_id(self, request, pk=None):
        profile: ResidentProfile = self.get_object()
        profile.gov_id = list(request.FILES.values())[0] # Get first file
        profile.save()
        return Response({'status': 'File uploaded'})

