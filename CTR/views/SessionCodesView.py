from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from CTR.models import Session, SessionCodesEarnings, SessionCodesMemos, SessionCodesDeductions
from CTR.serializers import SessionCodesEarningsSerializer, SessionCodesMemosSerializer, \
    SessionCodesDeductionsSerializer
from CTR.utils import handle_codes


class SessionCodesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, session_id):
        try:
            session = Session.objects.get(id=session_id)
        except Session.DoesNotExist:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)

        earnings = SessionCodesEarnings.objects.filter(session=session)
        memos = SessionCodesMemos.objects.filter(session=session)
        deductions = SessionCodesDeductions.objects.filter(session=session)

        earnings_serializer = SessionCodesEarningsSerializer(earnings, many=True)
        memos_serializer = SessionCodesMemosSerializer(memos, many=True)
        deductions_serializer = SessionCodesDeductionsSerializer(deductions, many=True)

        return Response({
            "session_id": session_id,
            "session_codes": {
                "earnings": earnings_serializer.data,
                "memos": memos_serializer.data,
                "deductions": deductions_serializer.data
            }
        })

    def post(self, request, session_id):
        try:
            session = Session.objects.get(id=session_id)
        except Session.DoesNotExist:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)

        earnings_data = request.data.get('session_codes', {}).get('earnings', [])
        memos_data = request.data.get('session_codes', {}).get('memos', [])
        deductions_data = request.data.get('session_codes', {}).get('deductions', [])

        handle_codes(SessionCodesEarnings, SessionCodesEarningsSerializer, earnings_data, session)
        handle_codes(SessionCodesMemos, SessionCodesMemosSerializer, memos_data, session)
        handle_codes(SessionCodesDeductions, SessionCodesDeductionsSerializer, deductions_data, session)

        return Response({"message": "Session codes processed successfully"}, status=status.HTTP_200_OK)
