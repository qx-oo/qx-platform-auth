from django.utils.module_loading import import_string
from qx_base.settings import get_settings


QX_PLATFORM_AUTH_SETTINGS = {
    "APPLE_AUTH": {
        "APPLE_KEY_ID": None,
        "APPLE_TEAM_ID": None,
        "APPLE_CLIENT_ID": None,
        "APPLE_CLIENT_SECRET": None,
        "APPLE_REDIRECT_URI": None,
    },
    "PLATFORM_AUTH_MODEL": None,
    "MINIAPP_TOKEN_KEY": "",
    "MINIAPP_TOKEN_SECRET": "",
    "MINIAPP_TOKEN_PROD_URL": "",
    "MINIAPP_PLATFORM_MAP": None,
}

platform_auth_settings = get_settings(
    'QX_PLATFORM_AUTH_SETTINGS', QX_PLATFORM_AUTH_SETTINGS)

_platform_map = {}
if platform_auth_settings.MINIAPP_PLATFORM_MAP:
    for platform, cls in platform_auth_settings.MINIAPP_PLATFORM_MAP.items():
        _platform_map[platform] = import_string(cls)

platform_auth_settings.MINIAPP_PLATFORM_MAP = _platform_map
