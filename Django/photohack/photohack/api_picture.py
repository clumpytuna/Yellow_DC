from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile

from rest_framework.response import Response
from rest_framework.status import \
    HTTP_400_BAD_REQUEST, \
    HTTP_404_NOT_FOUND

from .models_picture import Picture
from .api_ml import send_to_ml, receive_from_ml


def upload(request):
    """
    Upload a new image for processing

    :returns: ID of an uploaded picture
    :returns: Response object in case an exception happens
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

    process_picture(new_picture)

    return int(new_picture.id)


def result(request):
    """
    Check an image was processed.

    :returns: URL of a processed image or None if it is not yet ready
    :returns: Response object in case an exception happens
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
        if not process_picture(picture):
            return None

    return picture.processed.url


def process_picture(picture: Picture) -> bool:
    """
    Try to urge picture processing
    """
    # Temporary
    # send_to_ml(picture.id, picture.source.path)
    # new_path = receive_from_ml(picture.id)
    new_path = picture.source.path

    if new_path is None:
        return False

    with open(new_path, 'rb') as f:
        content = f.read()

    picture.processed.save(new_path.split('/')[-1], ContentFile(content))

    picture.save()
    picture.refresh_from_db()

    return True
