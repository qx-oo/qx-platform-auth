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
    "MINIAPP_AUTH": {},
    "MINIAPP_TOKEN_KEY": "",
    "MINIAPP_TOKEN_SECRET": "",
    "MINIAPP_TOKEN_PROD_URL": "",
}

platform_auth_settings = get_settings(
    'QX_PLATFORM_AUTH_SETTINGS', QX_PLATFORM_AUTH_SETTINGS)

minapp_auth = {}

for miniapp, cls in platform_auth_settings.MINIAPP_AUTH.items():
    if isinstance(cls, str):
        minapp_auth[miniapp] = import_string(cls)

platform_auth_settings.MINIAPP_AUTH = minapp_auth
