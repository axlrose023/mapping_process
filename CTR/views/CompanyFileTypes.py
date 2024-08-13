from rest_framework.response import Response
from rest_framework.views import APIView
from CTR.models import Company, SessionFileType
from rest_framework import status


class CompanyFileTypes(APIView):
    def get(self, request):
        company_id = request.data.get('company_id')
        if not company_id:
            return Response({"error": "company_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

        file_types = SessionFileType.objects.filter(session=company.session)

        file_types_list = [file_type.file_type for file_type in file_types]

        return Response({"file_types": file_types_list}, status=status.HTTP_200_OK)
