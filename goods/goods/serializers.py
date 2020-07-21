from rest_framework import serializers

from .models import Advertisement, Tag


class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = "__all__"


class AdvertisementShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = ("id", "title", "price", "date")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"
