# qx-platform-auth

my django project thirdparty platform auth

### Install:

    pip install -e git://github.com/qx-oo/qx-platform-auth.git@master#egg=qx-platform-auth

### Usage:

depends:

    qx-base >= 1.0.7

settings.py:

    INSTALLED_APPS = [
        ...
        'qx_base.qx_core',
        'qx_base.qx_rest',
        'qx_base.qx_user',
        'qx_platform_auth',
        ...
    ]

    PLATFORM_AUTH_APPLE_SETTINGS = {
        "APPLE_AUTH": {
            "APPLE_KEY_ID": 'test',
            "APPLE_TEAM_ID": 'test',
            "APPLE_CLIENT_ID": 'test',
            "APPLE_CLIENT_SECRET": 'test',
            "APPLE_REDIRECT_URI": 'test',
        },
        "PLATFORM_AUTH_MODEL": 'user.UserPlatform'
    }