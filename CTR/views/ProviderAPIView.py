from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from CTR.models import Provider
from CTR.serializers import ProviderSerializer


class ProviderListAPIView(APIView):
    """
    API view to retrieve list of providers.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        providers = Provider.objects.all()
        serializer = ProviderSerializer(providers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
