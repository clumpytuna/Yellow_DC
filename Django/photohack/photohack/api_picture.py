from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import \
    HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_504_GATEWAY_TIMEOUT
from .models_picture import Picture


@api_view(['POST'])
def upload(request):
    """
    Upload a new image for processing
    """

    try:
        uploaded_file = request.FILES['image']
    except KeyError:
        return Response("Please provide the parameter 'image' containing an image.", HTTP_400_BAD_REQUEST)

    new_picture = Picture()
    new_picture.save()
    new_picture.refresh_from_db()

    new_picture.source.save(
            str(new_picture.id) + '.' + str(uploaded_file.name).split(".")[-1],
            uploaded_file
    )
    new_picture.save()

    return Response({'id': new_picture.id})


@api_view(['GET'])
def download(request):
    """
    Check an image was processed and can be downloaded
    """

    try:
        file_id = int(request.GET['id'])
    except KeyError or ValueError:
        return Response("Please provide the parameter 'id' with file ID.", HTTP_400_BAD_REQUEST)

    try:
        picture = Picture.objects.get(id=file_id)
    except ObjectDoesNotExist:
        return Response(None, HTTP_404_NOT_FOUND)

    if picture.processed is None:
        return Response(None, HTTP_504_GATEWAY_TIMEOUT)

    return HttpResponseRedirect(picture.processed.url)
