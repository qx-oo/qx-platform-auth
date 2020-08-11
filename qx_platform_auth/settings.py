from django.conf import settings
from qx_base.qx_core.tools import DictInstance
from qx_base.settings import get_attr


PLATFORM_AUTH_MODEL = None

PLATFORM_AUTH_APPLE_SETTINGS = {
    "APPLE_KEY_ID": None,
    "APPLE_TEAM_ID": None,
    "APPLE_CLIENT_ID": None,
    "APPLE_CLIENT_SECRET": None,
    "APPLE_REDIRECT_URI": None,
}

_b_settings = PLATFORM_AUTH_APPLE_SETTINGS

_settings = getattr(settings, 'PLATFORM_AUTH_APPLE_SETTINGS',
                    PLATFORM_AUTH_APPLE_SETTINGS)

if _settings:
    _b_settings.update(_settings)


_b_settings['PLATFORM_AUTH_MODEL'] = getattr(
    settings, 'PLATFORM_AUTH_MODEL', PLATFORM_AUTH_MODEL)


platform_auth_settings = DictInstance(**PLATFORM_AUTH_APPLE_SETTINGS,
                                      PLATFORM_AUTH_MODEL=PLATFORM_AUTH_MODEL)
for key, val in _b_settings.items():
    setattr(platform_auth_settings, key, get_attr(val))
