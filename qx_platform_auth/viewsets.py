import json
from django.conf import settings
from rest_framework import viewsets, decorators
from rest_framework.permissions import (
    AllowAny, IsAuthenticated,
)
from qx_base.qx_user.viewsets import UserViewSet as BaseUserViewSet
from qx_base.qx_user.viewsets import UserPermission as BaseUserPermission
from qx_base.qx_rest.response import ApiResponse, ApiNotFoundResponse
from qx_base.qx_rest import mixins
from .settings import platform_auth_settings
from .serializers import (
    PlatformSigninSerializer,
    MiniappSigninSerializer,
    PlatformSignupSerializer,
    BindPlatformSerializer,
    PlatformSerializer,
    platform_model,
    MINIAPP_PLATFORM_MAP,
)


def miniapp_token(request):
    """
    Development query miniapp token by production
    ---
        key: settings key
        secret: settings secret
    """
    if not settings.PRODUCTION:
        raise ApiNotFoundResponse()
    if request.method == 'GET':
        req_data = request.GET
    else:
        try:
            req_data = json.loads(request.body)
        except Exception:
            raise ApiNotFoundResponse()

    key = req_data.get('key', '')
    secret = req_data.get('secret', '')

    if platform_auth_settings.MINIAPP_TOKEN_KEY != key or \
            platform_auth_settings.MINIAPP_TOKEN_SECRET != secret:
        return ApiNotFoundResponse()
    try:
        platform = req_data.get('platform', '')
        cls = MINIAPP_PLATFORM_MAP[platform]
    except Exception:
        return ApiNotFoundResponse()

    token = cls().get_access_token()
    if not token:
        return ApiNotFoundResponse()
    else:
        return ApiResponse({
            "access_token": token
        })


class UserPermission(BaseUserPermission):
    def has_permission(self, request, view):
        if view.action in [
                'signin_platform', 'signup_platform',
                'signin_miniapp']:
            return AllowAny().has_permission(request, view)
        return super().has_permission(request, view)


class UserViewSet(BaseUserViewSet):
    """

    signin_platform:
        三方平台登录

        三方平台登录

    signin_miniapp:
        小程序登录

        小程序登录

    signup_platform:
        三方平台注册(包含小程序)

        三方平台注册
    """
    __doc__ = BaseUserViewSet.__doc__ + __doc__

    permission_classes = (
        UserPermission,
    )

    def get_serializer_class(self):
        if self.action == 'signin_platform':
            return PlatformSigninSerializer
        elif self.action == 'signin_miniapp':
            return MiniappSigninSerializer
        elif self.action == 'signup_platform':
            return PlatformSignupSerializer
        return super().get_serializer_class()

    @decorators.action(methods=['post'], url_path='signin-platform',
                       detail=False)
    def signin_platform(self, request, *args, **kwargs):
        return ApiResponse(data=self._create(request, *args, **kwargs))

    @decorators.action(methods=['post'], url_path='signin-miniapp',
                       detail=False)
    def signin_miniapp(self, request, *args, **kwargs):
        return ApiResponse(data=self._create(request, *args, **kwargs))

    @decorators.action(methods=['post'], url_path='signup-platform',
                       detail=False)
    def signup_platform(self, request, *args, **kwargs):
        return ApiResponse(data=self._create(request, *args, **kwargs))


class PlatformViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,):
    """
    用户平台认证
    ---

    create:
        绑定三方平台

        绑定三方平台

    list:
        获取绑定的三方平台

        获取绑定的三方平台

    destroy:
        解除三方平台绑定

        解除三方平台绑定
    """

    permission_classes = (
        IsAuthenticated,
    )

    queryset = platform_model.objects.all()

    is_paginate = False
    cache_list = True
    cache_onlyuser_by_action = {
        "list": True,
    }

    def get_serializer_class(self):
        if self.action == 'create':
            return BindPlatformSerializer
        return PlatformSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.queryset.filter(user_id=self.request.user.id)
        return self.queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.user_id = None
        instance.save()
        return ApiResponse({})
