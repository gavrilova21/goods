from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Advertisement, Tag
from .serializers import (
    AdvertisementSerializer,
    AdvertisementShortSerializer,
    TagSerializer,
)


class AdvertisementList(ListCreateAPIView):
    """
    List all adverts, or create a new ad.
    """

    parser_class = (FileUploadParser,)
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer

    def get_queryset(self):
        ads = Advertisement.objects.all()
        tags = self.request.query_params.get("tags", [])
        min_price = self.request.query_params.get("min_price", None)
        max_price = self.request.query_params.get("max_price", None)
        st_date = self.request.query_params.get("st_date", None)
        end_date = self.request.query_params.get("end_date", None)
        if tags:
            tags = tags.split(",")
            ads = ads.filter(tags__in=tags).distinct()
        if min_price:
            ads = ads.filter(price__gte=min_price)
        if max_price:
            ads = ads.filter(price__lte=max_price)
        if st_date:
            ads = ads.filter(date__gte=st_date)
        if end_date:
            ads = ads.filter(date__lte=end_date)
        return ads


class AdvertisementDetail(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a ads instance.
    """

    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer

    def get(self, request, pk, format=None):
        ad = get_object_or_404(Advertisement, pk=pk)
        ad.increment_views()
        serializer = AdvertisementSerializer(ad)
        return Response(serializer.data)


class AdvertisementShort(RetrieveAPIView):
    """
    Get Short ads info
    """

    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementShortSerializer


class TagList(ListAPIView):
    """
    List all tags
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
