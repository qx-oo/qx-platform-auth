from qx_base.settings import get_settings


QX_PLATFORM_AUTH_SETTINGS = {
    "APPLE_AUTH": {
        "APPLE_KEY_ID": None,
        "APPLE_TEAM_ID": None,
        "APPLE_CLIENT_ID": None,
        "APPLE_CLIENT_SECRET": None,
        "APPLE_REDIRECT_URI": None,
    },
    "PLATFORM_AUTH_MODEL": None
}

platform_auth_settings = get_settings(
    'QX_PLATFORM_AUTH_SETTINGS', QX_PLATFORM_AUTH_SETTINGS)
