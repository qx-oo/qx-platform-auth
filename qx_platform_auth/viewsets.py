from rest_framework import viewsets, decorators
from rest_framework.permissions import (
    AllowAny, IsAuthenticated,
)
from qx_base.qx_user.viewsets import UserViewSet as BaseUserViewSet
from qx_base.qx_user.viewsets import UserPermission as BaseUserPermission
from qx_base.qx_rest.response import ApiResponse
from qx_base.qx_rest import mixins
from .serializers import (
    PlatformSigninSerializer,
    PlatformSignupSerializer,
    BindPlatformSerializer,
    PlatformSerializer,
    platform_model,
)


class UserPermission(BaseUserPermission):
    def has_permission(self, request, view):
        if view.action in ['signin_platform', 'signup_platform']:
            return AllowAny().has_permission(request, view)
        return super().has_permission(request, view)


class UserViewSet(BaseUserViewSet):
    """
    {}

    signin_platform:
        三方平台登录

        三方平台登录

    signup_platform:
        三方平台注册

        三方平台注册
    """.format(BaseUserViewSet.__doc__)

    permission_classes = (
        UserPermission,
    )

    def get_serializer_class(self):
        if self.action == 'signin_platform':
            return PlatformSigninSerializer
        elif self.action == 'signup_platform':
            return PlatformSignupSerializer
        return super().get_serializer_class()

    @decorators.action(methods=['post'], url_path='signin-platform',
                       detail=False)
    def signin_platform(self, request, *args, **kwargs):
        return ApiResponse(data=self._create(request, *args, **kwargs))

    @decorators.action(methods=['post'], url_path='signup-platform',
                       detail=False)
    def signup_platform(self, request, *args, **kwargs):
        return ApiResponse(data=self._create(request, *args, **kwargs))


class PlatformViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,):
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
            return self.queryset.filter(user=self.request.user)
        return self.queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.user_id = None
        instance.save()
        return ApiResponse({})
