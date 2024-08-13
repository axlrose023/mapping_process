from typing import Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from CTR.serializers import AvailableHeadersSerializer
from CTR.utils import SessionDataFetcher


class GetMappingsView(APIView):
    """
       Handles GET requests to retrieve extracted headers and saved mappings for a specific session.
    """

    def get(self, request: Any, session_id: int) -> Response:
        data = SessionDataFetcher.get_mappings(session_id)
        serializer = AvailableHeadersSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
