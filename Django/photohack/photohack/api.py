
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import \
    HTTP_400_BAD_REQUEST, \
    HTTP_422_UNPROCESSABLE_ENTITY
from .models_picture import Picture


@api_view(['POST'])
def upload(request):
    try:
        uploaded_file = request.FILES['image']
    except KeyError:
        return Response(None, HTTP_400_BAD_REQUEST)

    new_picture = Picture()
    new_picture.save()
    new_picture.refresh_from_db()

    new_picture.source.save(str(new_picture.id), uploaded_file)
    new_picture.save()

    return Response({'id': new_picture.id})


