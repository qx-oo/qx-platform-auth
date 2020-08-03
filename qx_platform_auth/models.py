from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.postgres.fields import JSONField


User = get_user_model()


class PlatformAuth_Meta:
    verbose_name = "PlatformAuth"
    verbose_name_plural = verbose_name
    unique_together = (('platform', 'user_id'), ('platform', 'openid'))


class PlatformAuth(models.Model):
    '''
    Platform user auth
    '''

    platform = models.CharField(
        verbose_name='平台', max_length=10, db_index=True)
    openid = models.CharField(
        verbose_name='Openid', max_length=50, unique=True)
    token = models.TextField(
        verbose_name='token', null=True)
    user_id = models.IntegerField(
        verbose_name="用户Id", null=True, blank=True)
    created = models.DateTimeField(
        verbose_name='创建时间', default=timezone.now, editable=False)
    extra_info = JSONField(
        verbose_name="信息", default=dict)

    class Meta:
        abstract = True
