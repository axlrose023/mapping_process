from rest_framework.response import Response
from rest_framework.views import APIView
from CTR.models import Company, SessionFileLink
from rest_framework import status


class CompanyFileLinks(APIView):
    def get(self, request):
        company_id = request.data.get('company_id')
        file_type = request.data.get('file_type')

        if not company_id or not file_type:
            return Response({"error": "company_id and file_type are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

        file_links = SessionFileLink.objects.filter(company=company, file_type=file_type).values_list('file_link',
                                                                                                      flat=True)

        if not file_links:
            return Response({"message": "No file links found for the given file type and company"},
                            status=status.HTTP_404_NOT_FOUND)

        return Response({"file_links": list(file_links)}, status=status.HTTP_200_OK)
