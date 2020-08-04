import requests
import logging
import json
import jwt
from django.utils import timezone
from .settings import platform_auth_settings


logger = logging.getLogger(__name__)


class WeiboAuth():
    """
    Weibo Auth
    """

    def auth(self, openid, access_token):
        result = requests.request(
            "POST",
            "https://api.weibo.com/oauth2/get_token_info",
            params={'access_token': access_token},
            timeout=20)
        j_data = json.loads(result.text)
        if str(j_data['uid']) == openid:
            return True, {
                "openid": openid,
            }
        else:
            return False, {
                "error_msg": "Auth error"
            }


class WechatAuth():
    """
    Wechat Auth
    """

    def auth(self, openid, access_token):
        result = requests.request(
            "GET",
            "https://api.weixin.qq.com/sns/auth",
            params={'access_token': access_token,
                    "openid": openid},
            timeout=20)
        j_data = json.loads(result.text)
        if j_data['errcode'] == 0:
            return True, {
                "openid": openid,
            }
        else:
            return False, {
                "error_msg": j_data['errmsg']
            }


class FacebookAuth():
    """
    Facebook Auth
    """

    def auth(self, openid, access_token):
        result = requests.request(
            "GET",
            "https://graph.facebook.com/me",
            params={'access_token': access_token, "fields": 'id'},
            timeout=20)
        j_data = json.loads(result.text)
        if j_data.get('id', None) == openid:
            return True, {
                "openid": openid,
            }
        else:
            return False, {
                "error_msg": j_data['error']['message']
            }


class GoogleAuth():
    """
    Google Auth
    """

    def auth(self, openid, access_token):
        result = requests.request(
            "GET",
            "https://www.googleapis.com/oauth2/v3/tokeninfo",
            params={'id_token': access_token},
            timeout=20)
        j_data = json.loads(result.text)
        if j_data.get('sub', None) == openid:
            return True, {
                "openid": openid,
            }
        else:
            return False, {
                "error_msg": j_data['error_description']
            }


class AppleAuth():
    """
    Apple Auth
    """

    url = 'https://appleid.apple.com/auth/token'

    def auth(self, openid, access_token):
        client_id, client_secret = self.get_key_and_secret()
        headers = {'content-type': "application/x-www-form-urlencoded"}
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': access_token,
            'grant_type': 'authorization_code',
            'redirect_uri': 'https://example-app.com/redirect'
        }
        resp = requests.post(self.url, data=data, headers=headers)
        resp_data = resp.json()
        id_token = resp_data.get('id_token', None)
        if id_token:
            decoded = jwt.decode(id_token, '', verify=False)
            email = None
            if not decoded.get('is_private_email', True):
                email = decoded.get('email')
            _openid = decoded.get('sub')
            if openid != _openid:
                return False, {
                    "error_msg": "Auth error"
                }
            return True, {
                'openid': _openid,
                'email': email
            }
        return False, {
            "error_msg": "Auth error"
        }

    def get_key_and_secret(self):
        headers = {
            'kid': platform_auth_settings.APPLE_KEY_ID
        }

        payload = {
            'iss': platform_auth_settings.APPLE_TEAM_ID,
            'iat': timezone.now(),
            'exp': timezone.now() + timezone.timedelta(days=180),
            'aud': 'https://appleid.apple.com',
            'sub': platform_auth_settings.APPLE_CLIENT_ID,
        }

        client_secret = jwt.encode(
            payload,
            platform_auth_settings.APPLE_CLIENT_SECRET,
            algorithm='ES256',
            headers=headers
        ).decode("utf-8")

        return platform_auth_settings.APPLE_CLIENT_ID, client_secret

    def get_user_details(self, response):
        email = response.get('email', None)
        details = {
            'email': email,
        }
        return details


APP_PLATFORM_MAP = {
    "weibo": WeiboAuth,
    "wechat": WechatAuth,
    "facebook": FacebookAuth,
    "google": GoogleAuth,
    "apple": AppleAuth,
}


class AppPlatform():

    def __init__(self):
        pass

    def auth(self, platform, openid, access_token):
        try:

            app_cls = APP_PLATFORM_MAP.get(platform)
            if not app_cls:
                return False, {
                    "error_msg": "Platform {} error".format(platform)
                }
            return app_cls().auth(openid, access_token)

        except requests.exceptions.ConnectTimeout:
            return False, {
                "error_msg": "Request timeout"
            }
        except KeyError:
            return False, {
                "error_msg": "Auth error"
            }
