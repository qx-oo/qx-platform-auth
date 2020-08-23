from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from qx_base.qx_core.tools import DictInstance
from qx_base.qx_user.tools import CodeMsg
from qx_base.qx_user.serializers import SignupSerializer
from qx_base.qx_rest.exceptions import SerializerFieldError
from .settings import platform_auth_settings
from .socialapps import APP_PLATFORM_MAP, AppPlatform


User = get_user_model()
platform_model = platform_auth_settings.PLATFORM_AUTH_MODEL


class PlatformSigninSerializer(serializers.Serializer):

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
    platform_code = serializers.CharField(
        label="Signup Code", read_only=True)

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
            is_send, code = CodeMsg(
                validated_data['openid'],
                _type="platform_signup").get_new_code()
            return DictInstance(
                **validated_data, **{
                    "is_register": False,
                    "token": None,
                    "extra_info": ret,
                    "platform_code": code,
                })
        else:
            token = user.get_new_token()
            return DictInstance(
                **validated_data, **{
                    "is_register": True,
                    "token": token,
                    "extra_info": ret,
                    "platform_code": None,
                })


class PlatformSignupSerializer(SignupSerializer):

    openid = serializers.CharField(
        label="Openid", write_only=True)
    platform = serializers.ChoiceField(
        label="Platform", choices=list(APP_PLATFORM_MAP.items()),
        write_only=True)
    platform_code = serializers.CharField(
        label="Platform Signup Code", max_length=10,
        write_only=True)

    def create(self, validated_data):

        openid = validated_data['openid']
        platform = validated_data['platform']
        platform_code = validated_data['platform_code']

        _code = CodeMsg(
            openid, _type='platform_signup').get_code()
        if platform_code != _code:
            raise SerializerFieldError(
                '验证码错误', field='code')

        platform_ins = platform_model.objects.filter(
            openid=openid,
            platform=platform).first()
        if not platform_ins:
            raise SerializerFieldError('openid error', field=openid)
        if platform_ins.user_id:
            raise SerializerFieldError(
                '已绑定用户', field='openid')

        with transaction.atomic():
            instance = super().create_user(validated_data)

            platform_ins.user_id = instance.id
            platform_ins.save()

        return instance


class BindPlatformSerializer(serializers.Serializer):

    id = serializers.IntegerField(
        label="Id", read_only=True)
    openid = serializers.CharField(
        label="Openid", max_length=250)
    access_token = serializers.CharField(
        label="Access Token", max_length=500)
    platform = serializers.ChoiceField(
        label="Platform", choices=list(APP_PLATFORM_MAP.items()))

    def create(self, validated_data):
        status, ret = AppPlatform().auth(**validated_data)
        if not status:
            raise serializers.ValidationError(ret['error_msg'])
        instance, _ = platform_model.objects.get_or_create(
            openid=validated_data['openid'],
            platform=validated_data['platform'],
            defaults={"extra_info": ret})

        instance.user_id = self.context['request'].user.id
        instance.save()
        return DictInstance(id=instance.id, **validated_data)


class PlatformSerializer(serializers.ModelSerializer):

    class Meta:
        model = platform_model
        fields = ('id', 'openid', 'platform', 'created',)
