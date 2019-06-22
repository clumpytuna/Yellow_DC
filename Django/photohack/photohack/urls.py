from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import url
from .api_picture import upload, download

urlpatterns = [
    url(r'^upload$', upload),
    url(r'^download$', download),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
