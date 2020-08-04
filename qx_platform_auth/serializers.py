from rest_framework import serializers
from .settings import platform_auth_settings


platform_model = platform_auth_settings.PLATFORM_MODEL_CLASS


class PlatformSerializer(serializers.ModelSerializer):

    class Meta:
        model = platform_model
        fields = ()
