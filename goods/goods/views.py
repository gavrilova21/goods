from django.http import Http404
from rest_framework import status
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Advertisement, Tag
from .serializers import (
    AdvertisementSerializer,
    AdvertisementShortSerializer,
    TagSerializer,
)


class AdvertisementList(APIView):
    """
    List all adverts, or create a new ad.
    """

    parser_class = (FileUploadParser,)

    def get(self, request):
        ads = Advertisement.objects.all()
        tags = self.request.query_params.get("tags", [])
        price = self.request.query_params.get("price", None)
        st_date = self.request.query_params.get("st_date", None)
        end_date = self.request.query_params.get("end_date", None)
        if tags:
            tags = tags.split(",")
            ads = ads.filter(tags__in=tags)
        if price:
            ads = ads.filter(price=price)
        if st_date:
            ads = ads.filter(date__gte=st_date)
        if end_date:
            ads = ads.filter(date__lte=end_date)
        serializer = AdvertisementSerializer(ads, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AdvertisementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdvertisementDetail(APIView):
    """
    Retrieve, update or delete a ads instance.
    """

    def get_object(self, pk):
        try:
            return Advertisement.objects.get(pk=pk)
        except Advertisement.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        ad = self.get_object(pk)
        ad.increment_views()
        serializer = AdvertisementSerializer(ad)
        return Response(serializer.data)

    def put(self, request, pk):
        ad = self.get_object(pk)
        serializer = AdvertisementSerializer(ad, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        ad = self.get_object(pk)
        ad.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdvertisementShort(APIView):
    """
    Get Short ads info
    """

    def get_object(self, pk):
        try:
            return Advertisement.objects.get(pk=pk)
        except Advertisement.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        ad = self.get_object(pk)
        serializer = AdvertisementShortSerializer(ad)
        return Response(serializer.data)


class TagList(APIView):
    """
    List all tags
    """

    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)
