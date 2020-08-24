from qx_platform_auth.minapps import WXMiniApp


class WXTestApp(WXMiniApp):

    platform = "testapp"

    def _get_appinfo(self):
        return ('appid_test',
                'appid_secret')
