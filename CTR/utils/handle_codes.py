from rest_framework.response import Response
from rest_framework import status


def handle_codes(model, serializer_class, data, session):
    model.objects.filter(session=session).delete()
    for item in data:
        item['session'] = session.id
        serializer = serializer_class(data=item)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return None
