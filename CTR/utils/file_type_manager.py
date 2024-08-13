from CTR.models import Session, SessionFileType

class FileTypeManager:
    @staticmethod
    def populate_file_types(session: Session, file_type: str) -> None:
        SessionFileType.objects.get_or_create(session=session, file_type=file_type)
