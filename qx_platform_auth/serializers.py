from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q
from django.db import transaction
from qx_base.qx_core.tools import DictInstance
from qx_base.qx_user.tools import CodeMsg, generate_random_account
from qx_base.qx_user.serializers import SignupSerializer
from qx_base.qx_rest.exceptions import SerializerFieldError
from .settings import platform_auth_settings
from .socialapps import APP_PLATFORM_MAP, AppPlatform


User = get_user_model()
platform_model = platform_auth_settings.PLATFORM_AUTH_MODEL


class SigninSerializer(serializers.Serializer):

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
    code = serializers.CharField(
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
                validated_data['openid'], _type="signup").get_new_code()
            return DictInstance(
                **validated_data, **{
                    "is_register": False,
                    "token": None,
                    "extra_info": ret,
                    "code": code,
                })
        else:
            token = user.get_new_token()
            return DictInstance(
                **validated_data, **{
                    "is_register": True,
                    "token": token,
                    "extra_info": ret,
                    "code": None,
                })


class PlatformSignupSerializer(SignupSerializer):

    openid = serializers.CharField(
        label="Openid")
    platform = serializers.ChoiceField(
        label="Platform", choices=list(APP_PLATFORM_MAP.items()))

    # def _check_user_exists(self, email, mobile, openid):
    #     account = email or mobile or openid
    #     if User.objects.filter(
    #             Q(email=account) | Q(mobile=account) | Q(account=account)
    #     ).exists():
    #         if email:
    #             raise SerializerFieldError(
    #                 '用户已存在', field='email')
    #         elif mobile:
    #             raise SerializerFieldError(
    #                 '用户已存在', field='mobile')
    #         else:
    #             raise SerializerFieldError(
    #                 '用户已存在', field='openid')

    def create(self, validated_data):
        account = validated_data.pop('account', None)
        mobile = validated_data.pop('mobile', None)
        email = validated_data.pop('email', None)
        code = validated_data.pop('code', None)
        password = validated_data.pop('password', None)
        userinfo = validated_data.pop('userinfo', None)

        openid = validated_data['openid']
        platform = validated_data['platform']

        if not email and not mobile and not account:
            raise serializers.ValidationError(
                'email, mobile and account empty')

        # self._check_user_exists(email, mobile, openid)

        platform_ins = None
        if openid:
            platform_ins = platform_model.objects.filter(
                openid=openid,
                platform=platform).first()
            if platform_ins.user_id:
                raise SerializerFieldError(
                    'user exists', field='openid')
            if not platform_ins:
                raise SerializerFieldError(
                    'openid error', field='openid')
            object_id = openid
        else:
            object_id = email or mobile

        user = User.query_user(account, email, mobile)
        if user:
            if password:
                auth_user = authenticate(
                    account=user.account, password=password)
                if not auth_user:
                    raise SerializerFieldError(
                        '密码错误', field='password')
        if code:
            _code = CodeMsg(
                object_id, _type='signup').get_code()
            if code != _code:
                raise SerializerFieldError(
                    '验证码错误', field='code')

        if not account:
            account = generate_random_account()

        # creaste user
        with transaction.atomic():
            instance = self._create_user(
                account, mobile, email, password, userinfo)
            if platform_ins:
                platform_ins.user_id = instance.id
                platform_ins.save()
        return instance


class BindPlatformSerializer(serializers.Serializer):

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
        return instance


class PlatformSerializer(serializers.ModelSerializer):

    class Meta:
        model = platform_model
        fields = ('id', 'openid', 'platform', 'created',)
