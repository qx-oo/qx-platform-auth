from django.conf import settings
from django.utils.module_loading import import_string
from qx_base.qx_core.tools import DictInstance


PLATFORM_AUTH_SETTINGS = {
    "APPLE_KEY_ID": None,
    "APPLE_TEAM_ID": None,
    "APPLE_CLIENT_ID": None,
    "APPLE_CLIENT_SECRET": None,
    "APPLE_REDIRECT_URI": None,
    "PLATFORM_MODEL_CLASS": None,
}

_b_settings = PLATFORM_AUTH_SETTINGS

_settings = getattr(settings, 'PLATFORM_AUTH_SETTINGS', PLATFORM_AUTH_SETTINGS)

if _settings:
    _b_settings.update(_settings)


def get_attr(key, val):
    if key.endswith('_CLASS'):
        if val:
            return import_string(val)
        else:
            raise ImportError('Settings {} import error.'.format(key))
    return val


platform_auth_settings = DictInstance(**PLATFORM_AUTH_SETTINGS)
for key, val in _b_settings.items():
    setattr(platform_auth_settings, key, get_attr(val))
