from django.urls import path, include
from rest_framework.routers import DefaultRouter
from qx_platform_auth import viewsets


router = DefaultRouter()
router.register('user', viewsets.UserViewSet)
router.register('platform', viewsets.PlatformViewSet)


urlpatterns_api = [
    path('', include(router.urls)),
]

urlpatterns = [
    path('api/tests/', include(urlpatterns_api)),
]
