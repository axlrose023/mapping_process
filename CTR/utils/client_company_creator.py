from CTR.models import Client, Session, Provider
from CTR.serializers import ClientSerializer, CompanySerializer, SessionSerializer
from rest_framework import status
from rest_framework.response import Response


class ClientCompanyCreator:
    @staticmethod
    def _create_session():
        session_serializer = SessionSerializer(data={})
        if session_serializer.is_valid():
            session = session_serializer.save()
            return session.id
        else:
            raise ValueError(session_serializer.errors)

    @staticmethod
    def create_client_and_company(client_name, company_name, provider_id, session_id=None):
        if not session_id:
            try:
                session_id = ClientCompanyCreator._create_session()
            except ValueError as e:
                return Response(e.args[0], status=status.HTTP_400_BAD_REQUEST)

        client_serializer = ClientSerializer(data={"client_name": client_name})
        if client_serializer.is_valid():
            client = client_serializer.save()
            company_data = {
                "company_name": company_name,
                "provider_id": provider_id,  # Note the use of provider_id here
                "session": session_id,
                "client": client.id
            }
            company_serializer = CompanySerializer(data=company_data)
            if company_serializer.is_valid():
                company_serializer.save()
                return Response({
                    "client": client_serializer.data,
                    "company": company_serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                client.delete()
                return Response(company_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(client_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def create_company_with_existing_client(client_id, company_name, provider_id, session_id=None):
        if not session_id:
            try:
                session_id = ClientCompanyCreator._create_session()
            except ValueError as e:
                return Response(e.args[0], status=status.HTTP_400_BAD_REQUEST)

        try:
            client = Client.objects.get(id=client_id)
            company_data = {
                "company_name": company_name,
                "provider_id": provider_id,  # Note the use of provider_id here
                "session": session_id,
                "client": client.id
            }
            company_serializer = CompanySerializer(data=company_data)
            if company_serializer.is_valid():
                company_serializer.save()
                return Response(company_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(company_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Client.DoesNotExist:
            return Response({"detail": "Client not found."}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def create_client_with_default_company(client_name, provider_id):
        """
        Create a new client and a default company.
        """
        try:
            provider = Provider.objects.get(id=provider_id)
        except Provider.DoesNotExist:
            return Response({"detail": "Provider not found."}, status=status.HTTP_404_NOT_FOUND)

        client_serializer = ClientSerializer(data={"client_name": client_name})
        if client_serializer.is_valid():
            client = client_serializer.save()

            # Create a default session for the company
            default_session = Session.objects.create(is_closed=False)

            # Create the default company for the new client
            company_data = {
                "company_name": "Default Company",
                "provider_id": provider.id,
                "session": default_session.id,
                "client": client.id
            }
            company_serializer = CompanySerializer(data=company_data)
            if company_serializer.is_valid():
                company_serializer.save()
                return Response({
                    "client": client_serializer.data,
                    "company": company_serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                client.delete()
                return Response(company_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(client_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def create_only_company(company_name, provider_id, client_id=None):
        try:
            session_id = ClientCompanyCreator._create_session()
        except ValueError as e:
            return Response(e.args[0], status=status.HTTP_400_BAD_REQUEST)

        company_data = {
            "company_name": company_name,
            "provider_id": provider_id,  # Note the use of provider_id here
            "session": session_id,
            "client": client_id
        }
        company_serializer = CompanySerializer(data=company_data)
        if company_serializer.is_valid():
            company_serializer.save()
            return Response(company_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(company_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
