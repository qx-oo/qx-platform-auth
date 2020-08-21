import logging
import requests
from django.conf import settings
from .settings import platform_auth_settings

logger = logging.getLogger(__name__)


miniapp_map = platform_auth_settings.MINIAPP_AUTH


class RefreshMiniAppTokenTask():
    """
    update miniapp access token
    """

    def get_prod_token(self, url):
        try:
            resp = requests.get(url)
            data = resp.json()
            token = data['data']['access_token']
        except Exception:
            logger.exception(
                "{} prod get fail: {}".format(
                    self.__class__.__name__, resp.text))
            return None
        return token

    def run(self):
        for platform, cls in miniapp_map.items():
            try:
                run_app = cls()
                if settings.PRODUCTION:
                    token = cls().refresh_token()
                else:
                    url = "{}?key={}&secret={}".format(
                        platform_auth_settings.MINIAPP_TOKEN_PROD_URL,
                        platform_auth_settings.MINIAPP_TOKEN_KEY,
                        platform_auth_settings.MINIAPP_TOKEN_SECRET,
                    )
                    token = self.get_prod_token(url)
                if token:
                    run_app.set_access_token(token)
                else:
                    logger.error(
                        'RefreshAccessToken Error: {}'.format(cls.__name__))
            except Exception:
                logger.exception("{} WxPushMsg".format(
                    self.__class__.__name__))
