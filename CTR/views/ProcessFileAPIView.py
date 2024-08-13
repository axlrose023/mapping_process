from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from CTR.models import Company
from CTR.serializers import ProcessFileSerializer

from CTR.utils import SessionManager, FileTypeManager, SessionProcessor, SessionDataFetcher


class ProcessFileAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request) -> Response:
        serializer = ProcessFileSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            session = SessionManager.get_session(data['session_id'])
            if not session:
                return Response({"error": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

            try:
                company = Company.objects.get(session_id=data['session_id'])
                provider_name = company.provider.provider_name
            except Company.DoesNotExist:
                return Response({"error": "Company not found for the given session ID."},
                                status=status.HTTP_404_NOT_FOUND)

            FileTypeManager.populate_file_types(session, data['file_type'])

            # Handle main file uploads
            uploaded_files = data['file']
            print(f"Uploaded files: {[file.name for file in uploaded_files]}")

            # Handle mapping files upload
            mapping_files = data['mapping_files']
            print(f"Mapping files: {[file.name for file in mapping_files]}")

            try:
                processor = SessionProcessor()
                result = processor.process_uploaded_files(uploaded_files, provider_name, session.id)
                headers = result['headers']
                payroll_data = result['payroll_data']

                # Populate extracted headers with fallback logic
                processor.populate_extracted_headers(session.id, headers, data['file_type'], company)

                # Populate session codes
                processor.populate_session_codes(session.id, mapping_files)

                # Fetch response data
                response_data = SessionDataFetcher.get_mappings(session.id)
                return Response({"data": response_data, "PayrollData": payroll_data}, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
