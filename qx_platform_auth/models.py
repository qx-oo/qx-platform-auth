from django.db import models
from django.db.models import JSONField
from qx_base.qx_rest.models import RestModel


class PlatformAuth_Meta:
    verbose_name = "PlatformAuth"
    verbose_name_plural = verbose_name
    unique_together = (('platform', 'user_id'), ('platform', 'openid'))


class PlatformAuth(RestModel):
    '''
    Platform user auth
    '''

    platform = models.CharField(
        verbose_name='平台', max_length=10, db_index=True)
    openid = models.CharField(
        verbose_name='Openid', max_length=50, unique=True)
    user_id = models.IntegerField(
        verbose_name="用户Id", null=True, blank=True, db_index=True)
    extra_info = JSONField(
        verbose_name="信息", default=dict)

    REST_CACHE_CLASS = {
        "default": {
            "PlatformViewSet": {
                "list_action": [
                    "list"
                ],
                "field_only": True,
                "field_name": "user_id"
            }
        },
        "reload_data": True,
    }

    class Meta:
        abstract = True
