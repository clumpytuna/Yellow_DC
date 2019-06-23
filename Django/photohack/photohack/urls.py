from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import url

from .views import user_upload, user_result
from .views import IndexView, WaitView

urlpatterns = [
    url(r'^$', IndexView.as_view()),
    url(r'^wait$', WaitView.as_view()),
    url(r'^upload$', user_upload),
    url(r'^result$', user_result),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
