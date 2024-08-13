from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from CTR.serializers import UpdateHeadersSerializer
from CTR.models import SessionFileLink, Company, Session, Client
from CTR.utils import SessionMappingUpdater


class UpdateMappingsView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, session_id: int) -> Response:
        serializer = UpdateHeadersSerializer(data=request.data.get('data'))
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                session = Session.objects.get(id=session_id)
                company = Company.objects.get(session=session)
                client = company.client

                # Update the session mappings
                SessionMappingUpdater.update_session_mappings(
                    session_id,
                    data.get('earnings_mappings', []),
                    data.get('deductions_mappings', []),
                    data.get('taxes_mappings', [])
                )

                # Store the provided file link
                file_link = data.get('file_link')
                file_type = data.get('file_type')

                SessionFileLink.objects.create(
                    session=session,
                    company=company,
                    client=client,
                    file_type=file_type,
                    file_link=file_link
                )

                return Response({"message": "Mappings updated and file link saved successfully."},
                                status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
