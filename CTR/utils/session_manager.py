from typing import Optional
from CTR.models import Session

class SessionManager:
    @staticmethod
    def get_session(session_id: int) -> Optional[Session]:
        try:
            return Session.objects.get(id=session_id)
        except Session.DoesNotExist:
            return None
