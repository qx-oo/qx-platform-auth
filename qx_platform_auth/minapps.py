import json
import logging
import requests
import urllib
from django.conf import settings
from qx_base.qx_core.storage import RedisClient

logger = logging.getLogger(__name__)


class MinAppMixin():
    """
    Mini App
    ---
    """

    def get_user_cache_key(self, token):
        return "user:minapp:{}:token:{}".format(
            self.platform, token), 60 * 60 * 24

    def get_glb_cache_key(self):
        return "glb:minapp:{}:token".format(self.platform), 60 * 60 * 2

    @property
    def platform(self):
        raise NotImplementedError

    def get_info_by_token(self, token: str) -> (bool, dict):
        raise NotImplementedError

    def cache_info(self, token: str, info: dict):
        client = RedisClient().get_conn()
        key, ts = self.user_cache_key
        key = key.format(self.platform, token)
        client.set(key, json.dumps(info), ts)

    def clear_cache_info(self, token: str):
        client = RedisClient().get_conn()
        key, ts = self.user_cache_key

        key = key.format(self.platform, token)
        client.delete(key)

    def get_info(self, token: str) -> dict:
        # TODO: 特别测试
        if token == "shawn_test_16608800604":
            return {
                "openid": "shawn_test_16608800604"
            }
        client = RedisClient().get_conn()
        key, ts = self.user_cache_key
        info = client.get(key.format(self.platform, token))
        if info is None:
            return None
        return json.loads(info)

    def set_access_token(self, token):
        glb_key, ts = self.get_glb_cache_key()
        client = RedisClient().get_conn()
        client.set(glb_key, token, ts)

    def get_access_token(self) -> str:
        """
        Get wechat api access token
        """
        glb_key, ts = self.get_glb_cache_key()
        client = RedisClient().get_conn()
        token = client.get(glb_key)
        if token:
            return token
        token = self.refresh_token()
        if token:
            client.set(glb_key, token, ts)
            return token
        else:
            return token


class WXMinApp(MinAppMixin):
    '''
    wechat mini app
    ---
    example:

        class WXWeightApp(WXAppApi):

            platform = "test_app"

            def _get_appinfo(self):
                return (settings.WX_WEIGHT_APPID,
                        settings.WX_WEIGHT_SECRET)
    '''

    domain = "https://api.weixin.qq.com"

    def _get_appinfo(self):
        raise NotImplementedError

    def send_template_msg(self, openid, form_id, template_id, data, page=''
                          ) -> bool:
        """
        推送模版消息
        """
        access_token = self.get_access_token()
        url = "{}/cgi-bin/message/wxopen/template/send".format(self.domain)
        url = "{}?access_token={}".format(url, access_token)
        json_data = {
            'touser': openid,
            'template_id': template_id,
            'page': page,
            'form_id': form_id,
            'data': data,
        }
        try:
            response = requests.post(url, json=json_data)
            json_data = json.loads(response.text)
            logger.info("{} send msg response: {}".format(
                self.platform, json_data))
        except Exception:
            logger.exception("{} send msg".format(self.platform))
            return False
        if not json_data.get('errcode'):
            return True
        else:
            return False

    def send_subscribe_msg(self, openid, template_id, data, page="") -> bool:
        """
        推送订阅消息
        """
        access_token = self.get_access_token()
        url = "{}/cgi-bin/message/subscribe/send".format(self.domain)
        url = "{}?access_token={}".format(url, access_token)
        json_data = {
            'touser': openid,
            'template_id': template_id,
            'page': page,
            'data': data,
        }
        if not settings.PRODUCTION:
            json_data['miniprogram_state'] = 'trial'
        try:
            response = requests.post(url, json=json_data)
            res_data = json.loads(response.text)
            logger.info(
                "{} send subscribe msg request: {}, response: {}".format(
                    self.platform, json_data, res_data))
        except Exception:
            logger.exception("{} send subscribe msg".format(self.platform))
            return False, "send_subscribe_msg exception"
        if not res_data.get('errcode'):
            return True, ""
        else:
            return False, res_data.get('errmsg', "unknown")

    def get_info_by_token(self, token: str) -> (bool, dict):
        """
        {
            openid	string	用户唯一标识
            session_key	string	会话密钥
            unionid	string	用户在开放平台的唯一标识符
            errcode	number	错误码
            errmsg	string	错误信息
        }
        """
        appid, secret = self._get_appinfo()
        url = "{}/sns/jscode2session".format(self.domain)
        url = "{}?appid={}&secret={}&js_code={}&grant_type=authorization_code"\
            .format(url, appid, secret, token)
        try:
            response = requests.get(url, timeout=20)
            json_data = json.loads(response.text)
            logger.info("{} verify response: {}, url: {}".format(
                self.platform, json_data, url))
        except Exception:
            logger.exception("{} token verify".format(self.platform))
            return False, None
        if not json_data.get('errcode'):
            self.cache_info(token, json_data)
            return True, json_data
        return False, None

    def refresh_token(self):
        appid, secret = self._get_appinfo()
        if not settings.PRODUCTION:
            return None
        url = "{}/cgi-bin/token".format(self.domain)
        url = "{}?grant_type=client_credential&appid={}&secret={}"\
            .format(url, appid, secret)
        try:
            response = requests.get(url, timeout=15)
            json_data = response.json()
            logger.info(
                "{} get_access_token response: {}".format(
                    self.platform, json_data))
        except Exception:
            logger.exception("{} get_access_token".format(self.platform))
            return None
        if not json_data.get('errcode'):
            access_token = json_data['access_token']
            return access_token
        else:
            logger.error("{} get_access_token".format(self.platform))
            return None

    def get_qrcode(self, filename: str, page: str, params: dict,
                   width: int = 430, extra={}) -> str:
        """
        Get mini app qrcode by params
        ----
        page: page/index/index
        params: {'id': 101}
        filename: 'test'
        width: default 430, min 280, max 1280
        """
        url = "{}/wxa/getwxacodeunlimit".format(self.domain)
        params = urllib.parse.urlencode(params)
        req_data = {
            "page": page,
            "scene": params,
            "width": width,
        }

        try:
            response = requests.post("{}?access_token={}".format(
                url, self.get_access_token()), timeout=20, json=req_data)
            _type = response.headers['Content-Type']
            resp_data = response.content
        except Exception:
            logger.exception("wechat get_qrcode")
            return None
        if _type == 'image/jpeg':
            buffer = resp_data
            return self._deal_qrcode(filename, buffer)
        else:
            logger.warning("get_qrcode response: {}".format(resp_data))
            return None
        return None

    def _deal_qrcode(self, filename: str, buffer: str) -> str:
        """
        upload qrcode
        ---
        example:
            return AutoOssStorage().put_bytes(
                "wechat/qrcode/{}.jpeg".format(filename),
                buffer,
            )
        """
        raise NotImplementedError
