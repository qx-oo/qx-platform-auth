# qx-platform-auth

my django project thirdparty platform auth

### Install:

    pip install -e git://github.com/qx-oo/qx-platform-auth.git@master#egg=qx-platform-auth

### Usage:

depends:

    qx-base >= 1.0.8

settings.py:

    INSTALLED_APPS = [
        ...
        'qx_base.qx_core',
        'qx_base.qx_rest',
        'qx_base.qx_user',
        'qx_platform_auth',
        ...
    ]

    PRODUCTION = True

    QX_PLATFORM_AUTH_SETTINGS = {
        "APPLE_AUTH": {
            "APPLE_KEY_ID": 'test',
            "APPLE_TEAM_ID": 'test',
            "APPLE_CLIENT_ID": 'test',
            "APPLE_CLIENT_SECRET": 'test',
            "APPLE_REDIRECT_URI": 'test',
        },
        "PLATFORM_AUTH_MODEL": 'user.UserPlatform',
        "MINIAPP_TOKEN_KEY": "test_key",
        "MINIAPP_TOKEN_SECRET": "test_secret",
        "MINIAPP_TOKEN_PROD_URL": "https://127.0.0.1:8000/user/miniapp/accesstoken/",
        "MINIAPP_PLATFORM_MAP": {
            "testapp": "qx_test.user.miniapps.WXTestApp",
        }
    }

    CELERY_BEAT_SCHEDULE = {
        ...
        'RefreshAccessTokenTask': {
            'task': 'qx_platform_auth.tasks.RefreshMiniAppTokenTask',
            'schedule': access_token_crontab,
        },
        ...
    }

mini app.py:

    from qx_platform_auth.miniapps import WXMiniApp

    class WXTestApp(WXMiniApp):

        platform = "testapp"

        def _get_appinfo(self):
            return ('appid_test',
                    'appid_secret')

