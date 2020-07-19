from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from .views import AdvertisementDetail, AdvertisementList, AdvertisementShort, TagList

schema_view = get_schema_view(
    openapi.Info(
        title="Goods API", default_version="v1", description="Avito (Walmart version)",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("ads/", AdvertisementList.as_view()),
    path("ads/<int:pk>/", AdvertisementDetail.as_view()),
    path("ads/<int:pk>/short", AdvertisementShort.as_view()),
    path("tags/", TagList.as_view()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
