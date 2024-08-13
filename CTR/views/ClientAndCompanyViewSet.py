from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from CTR.models import Client, Company
from CTR.serializers import ClientSerializer, CompanySerializer
from CTR.utils import ClientCompanyCreator


class ClientViewSet(viewsets.ModelViewSet):
    """
    A viewset for listing, creating, and retrieving clients.
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Create a new client, company, or both.
        """
        client_name = request.data.get("client_name")
        company_name = request.data.get("company_name")
        provider_id = request.data.get("provider_id")
        session_id = request.data.get("session_id")
        client_id = request.data.get("client")

        if client_name and provider_id:
            if company_name:
                return ClientCompanyCreator.create_client_and_company(client_name, company_name, provider_id,
                                                                      session_id)
            else:
                return ClientCompanyCreator.create_client_with_default_company(client_name, provider_id)
        elif client_id and company_name and provider_id:
            return ClientCompanyCreator.create_company_with_existing_client(client_id, company_name, provider_id,
                                                                            session_id)
        elif company_name and provider_id:
            return ClientCompanyCreator.create_only_company(company_name, provider_id, client_id)
        else:
            return Response({"detail": "Invalid data provided."}, status=status.HTTP_400_BAD_REQUEST)


class ClientCompaniesView(APIView):
    """
    A view to list all companies for a specific client or all companies if client_id is not specified.
    """
    permission_classes = [AllowAny]

    def get(self, request, client_id=None):
        if client_id:
            try:
                client = Client.objects.get(id=client_id)
            except Client.DoesNotExist:
                return Response({"error": "Client not found."}, status=status.HTTP_404_NOT_FOUND)
            companies = Company.objects.filter(client=client)
        else:
            companies = Company.objects.all()

        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
