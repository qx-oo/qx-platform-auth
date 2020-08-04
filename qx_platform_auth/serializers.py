from rest_framework import serializers
from django.contrib.auth import get_user_model
from qx_base.qx_core.tools import DictInstance
from qx_base.qx_core.storage import ProxyCache
from .settings import platform_auth_settings
from .socialapps import APP_PLATFORM_MAP, AppPlatform


User = get_user_model()
platform_model = platform_auth_settings.PLATFORM_MODEL_CLASS


class SigninSerializer(serializers.Serializer):

    CACHE_KEY = ""

    openid = serializers.CharField(
        label="Openid", max_length=250)
    access_token = serializers.CharField(
        label="Access Token", max_length=500)
    platform = serializers.ChoiceField(
        label="Platform", choices=list(APP_PLATFORM_MAP.items()))
    token = serializers.CharField(
        label="Token", read_only=True)
    is_register = serializers.BooleanField(
        label="Is register", read_only=True)
    extra_info = serializers.JSONField(
        label="Extra Info(email, mobile...)", read_only=True)

    def create(self, validated_data):
        status, ret = AppPlatform().auth(**validated_data)
        if not status:
            raise serializers.ValidationError(ret['error_msg'])
        instance, _ = platform_model.objects.get_or_create(
            openid=validated_data['openid'],
            platform=validated_data['platform'],
            defaults={"extra_info": ret})
        user = None
        if instance.user_id:
            user = User.objects.filter(id=instance.user_id).first()
        if not user:
            ProxyCache("")
            return DictInstance(
                **validated_data, **{
                    "is_register": False,
                    "token": None,
                    "extra_info": ret,
                })
        else:
            token = user.get_new_token()
            return DictInstance(
                **validated_data, **{
                    "is_register": True,
                    "token": token,
                    "extra_info": ret,
                })


class PlatformSerializer(serializers.ModelSerializer):

    class Meta:
        model = platform_model
        fields = ()
