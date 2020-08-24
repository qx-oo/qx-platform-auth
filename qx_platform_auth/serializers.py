import logging
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from qx_base.qx_core.tools import DictInstance
from qx_base.qx_user.tools import CodeMsg
from qx_base.qx_rest.serializers import SafeJSONField
from qx_base.qx_user.serializers import SignupSerializer
from qx_base.qx_rest.exceptions import SerializerFieldError
from .settings import platform_auth_settings
from .socialapps import APP_PLATFORM_MAP, AppPlatform
from .miniapps import MiniAppDataDecrypt

logger = logging.getLogger(__name__)


User = get_user_model()
platform_model = platform_auth_settings.PLATFORM_AUTH_MODEL
MINIAPP_PLATFORM_MAP = platform_auth_settings.MINIAPP_PLATFORM_MAP


all_platform = list(APP_PLATFORM_MAP.keys()) + \
    list(MINIAPP_PLATFORM_MAP.keys())


class PlatformSigninSerializer(serializers.Serializer):

    openid = serializers.CharField(
        label="Openid", max_length=250)
    access_token = serializers.CharField(
        label="Access Token", max_length=500)
    platform = serializers.ChoiceField(
        label="Platform", choices=list(APP_PLATFORM_MAP.keys()))
    token = serializers.CharField(
        label="Token", read_only=True)
    is_register = serializers.BooleanField(
        label="Is register", read_only=True)
    extra_info = serializers.JSONField(
        label="Extra Info(email, mobile...)", read_only=True)
    platform_code = serializers.CharField(
        label="Signup Code", read_only=True)

    def create(self, validated_data):
        openid = validated_data['openid']
        platform = validated_data['platform']
        status, ret = AppPlatform().auth(**validated_data)
        if not status:
            raise serializers.ValidationError(ret['error_msg'])
        instance, _ = platform_model.objects.get_or_create(
            openid=openid,
            platform=platform,
            defaults={"extra_info": ret})
        user = None
        if instance.user_id:
            user = User.objects.filter(id=instance.user_id).first()
        if not user:
            is_send, code = CodeMsg(
                "{}_{}".format(platform, openid),
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
        label="Platform", choices=list(all_platform),
        write_only=True)
    platform_code = serializers.CharField(
        label="Platform Signup Code", max_length=10,
        write_only=True)

    def create(self, validated_data):

        openid = validated_data['openid']
        platform = validated_data['platform']
        platform_code = validated_data['platform_code']

        _code = CodeMsg(
            "{}_{}".format(platform, openid),
            _type='platform_signup').get_code()
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


class MiniappSigninSerializer(serializers.Serializer):

    encrypted_data = SafeJSONField(
        label="加密数据, wechat: {'iv': '', 'encrypted_data': '', 'code': ''}",
        include_fields=['code', 'encrypted_data', 'iv'],
        required_fields=['code', 'encrypted_data', 'iv'],
        max_json_length=5000,
        write_only=True,
    )
    platform = serializers.ChoiceField(
        label="Platform", choices=list(MINIAPP_PLATFORM_MAP.keys()))

    token = serializers.CharField(
        label="Token", read_only=True)
    is_register = serializers.BooleanField(
        label="Is register", read_only=True)
    extra_info = serializers.JSONField(
        label="Extra Info(email, mobile...)", read_only=True)
    platform_code = serializers.CharField(
        label="Signup Code", read_only=True)

    def wxminiapp_decrypt(self, cls, validated_data, appid):
        encrypted_data = validated_data.pop('encrypted_data', None)
        extra_info = {}
        status, info = cls().get_info_by_token(
            encrypted_data.get('code'))
        if not status or not info.get('session_key'):
            raise SerializerFieldError(
                'encrypted_data code error', field='encrypted_data')
        session_key = info.get('session_key')
        try:
            data = MiniAppDataDecrypt(appid, session_key).decrypt(
                encrypted_data.get('encrypted_data'),
                encrypted_data.get('iv'),
            )
            extra_info['decrypt_info'] = data
            extra_info['openid'] = data['openId']
            extra_info['nick_name'] = data['nickName']
            extra_info['country'] = data['country']
            extra_info['city'] = data['city']
            extra_info['province'] = data['province']
            extra_info['gender'] = data['gender']
            extra_info['avatar'] = data['avatarUrl']
        except Exception:
            logger.exception("decrypted_data")
            raise SerializerFieldError(
                'encrypted_data decrypt error', field='encrypted_data')
        return data['openId'], extra_info

    def create(self, validated_data):
        platform = validated_data['platform']
        cls = MINIAPP_PLATFORM_MAP.get(platform)
        appid, _ = cls()._get_appinfo()
        # TODO: add other nimi app support, wechat miniapp only
        openid, extra_info = self.wxminiapp_decrypt(
            cls, validated_data, appid)

        instance, _ = platform_model.objects.get_or_create(
            openid=openid,
            platform=platform,
            defaults={"extra_info": extra_info})
        user = None
        if instance.user_id:
            user = User.objects.filter(id=instance.user_id).first()
        if not user:
            is_send, code = CodeMsg(
                "{}_{}".format(platform, openid),
                _type="platform_signup").get_new_code()
            return DictInstance(
                **validated_data, **{
                    "is_register": False,
                    "token": None,
                    "extra_info": extra_info,
                    "platform_code": code,
                })
        else:
            token = user.get_new_token()
            return DictInstance(
                **validated_data, **{
                    "is_register": True,
                    "token": token,
                    "extra_info": extra_info,
                    "platform_code": None,
                })


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


class MiniAppSigninSerializer(serializers.Serializer):

    platform = serializers.ChoiceField(
        label="Platform", choices=list(APP_PLATFORM_MAP.items()))
    encrypted_info = SafeJSONField(
        include_fields=['code', 'encrypted_data', 'iv'],
        max_json_length=5000,
        label="加密数据, wechat: {'iv': 123, 'encrypted_data': xxx}",
        write_only=True, required=False)

    def _decrypt(self):
        MiniAppDataDecrypt().decrypt()

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
