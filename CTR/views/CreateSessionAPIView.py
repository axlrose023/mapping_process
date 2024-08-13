from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from CTR.models import Company
from CTR.serializers import SessionSerializer, SessionFileTypeSerializer, CompanySerializer


class CreateSessionAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to create a session and session file type, update the company with the new session ID,
        and return the session ID.
        """
        session_data = {
            "is_closed": request.data.get("is_closed", False)
        }

        # Serialize the session data
        session_serializer = SessionSerializer(data=session_data)
        if session_serializer.is_valid():
            # Save the session if data is valid
            session = session_serializer.save()

            # Prepare data for creating a new session file type
            file_type_data = {
                "session": session.id,
                "file_type": request.data.get("file_type")
            }

            # Serialize the session file type data
            file_type_serializer = SessionFileTypeSerializer(data=file_type_data)
            if file_type_serializer.is_valid():
                # Save the session file type if data is valid
                file_type_serializer.save()

                # Update the company with the new session ID
                if "company_id" in request.data:
                    try:
                        company = Company.objects.get(id=request.data.get("company_id"))
                        company.session = session
                        company.save()

                        return Response({
                            "session": session_serializer.data,
                            "file_type": file_type_serializer.data,
                            "company": CompanySerializer(company).data
                        }, status=status.HTTP_201_CREATED)
                    except Company.DoesNotExist:
                        return Response({"detail": "Company not found."}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({
                        "session": session_serializer.data,
                        "file_type": file_type_serializer.data
                    }, status=status.HTTP_201_CREATED)
            else:
                return Response(file_type_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(session_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
