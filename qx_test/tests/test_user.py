import pytest
import json
from qx_platform_auth.viewsets import UserViewSet, PlatformViewSet
from qx_base.qx_core.tools import DictInstance
from qx_test.user.models import User, UserPlatform


class TestUserViewSet:

    def setup_class(self):
        self.url = "/api/tests/"
        self.viewset = UserViewSet

    @pytest.mark.django_db
    def test_signin_platform(self, rf, mocker, user_data_init):
        url = '{}/user/signin-platform/'.format(self.url)

        req_data = {
            'openid': 'test_openid',
            'access_token': 'test_token',
            'platform': 'wechat',
        }
        mocker.patch(
            "qx_platform_auth.socialapps.requests.get",
            return_value=DictInstance(text=json.dumps({"errcode": 0})))
        request = rf.post(
            url, data=req_data,
            content_type='application/json')
        response = self.viewset.as_view({'post': 'signin_platform'})(request)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert not data['data']['is_register']

        user = User.objects.all().first()
        UserPlatform.objects.filter(
            openid='test_openid').update(user_id=user.id)

        request = rf.post(
            url, data=req_data,
            content_type='application/json')
        response = self.viewset.as_view({'post': 'signin_platform'})(request)
        data = json.loads(response.content)
        assert data['data']['token']

    @pytest.mark.django_db
    def test_signin_miniapp(self, rf, mocker, user_data_init):
        url = '{}/user/signin-miniapp/'.format(self.url)

        req_data = {
            'encrypted_data': {
                'iv': '123',
                'encrypted_data': '123',
                'code': '123'},
            'platform': 'testapp',
        }

        ret = {
            'openId': 'testapp_openid',
            'nickName': 'testname',
            'country': 'testcountry',
            'city': 'testcity',
            'province': 'testprovince',
            'gender': 'testgender',
            'avatarUrl': 'testavatarUrl',
        }
        mocker.patch(
            "qx_platform_auth.serializers.MiniappSigninSerializer.wxminiapp_decrypt",  # noqa
            return_value=('testapp_openid', ret))
        request = rf.post(
            url, data=req_data,
            content_type='application/json')
        response = self.viewset.as_view({'post': 'signin_miniapp'})(request)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert not data['data']['is_register']

        user = User.objects.all().first()
        UserPlatform.objects.filter(
            openid='testapp_openid').update(user_id=user.id)

        request = rf.post(
            url, data=req_data,
            content_type='application/json')
        response = self.viewset.as_view({'post': 'signin_miniapp'})(request)
        data = json.loads(response.content)
        assert data['data']['token']

    @pytest.mark.django_db
    def test_signup_platform(self, rf, mocker, user_data_init):
        url = '{}/user/signin-platform/'.format(self.url)

        req_data = {
            'openid': 'test_openid',
            'access_token': 'test_token',
            'platform': 'wechat',
        }
        mocker.patch(
            "qx_platform_auth.socialapps.requests.get",
            return_value=DictInstance(text=json.dumps({"errcode": 0})))
        request = rf.post(
            url, data=req_data,
            content_type='application/json')
        response = self.viewset.as_view({'post': 'signin_platform'})(request)
        data = json.loads(response.content)
        assert data['data']['platform_code']

        url = '{}/user/signup-platform/'.format(self.url)

        req_data = {
            "openid": "test_openid",
            "mobile": '18866668000',
            "password": "12345678",
            'platform': 'wechat',
            "platform_code": data['data']['platform_code'],
            "userinfo": {
                "name": "test_user",
                "age": 15,
            }
        }

        mocker.patch(
            "qx_platform_auth.socialapps.requests.get",
            return_value=DictInstance(text=json.dumps({"errcode": 0})))
        request = rf.post(
            url, data=req_data,
            content_type='application/json')
        # request = signin_request(url, "post", data=data)
        response = self.viewset.as_view({'post': 'signup_platform'})(request)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['data']['token']


class TestPlatformViewSet:

    def setup_class(self):
        self.url = "/api/tests/"
        self.viewset = PlatformViewSet

    def test_bind(self, mocker, signin_request):
        url = '{}/user/signin-platform/'.format(self.url)

        url = '{}/platform/'.format(self.url)

        req_data = {
            'openid': 'test_openid',
            'access_token': 'test_token',
            'platform': 'wechat',
        }

        mocker.patch(
            "qx_platform_auth.socialapps.requests.get",
            return_value=DictInstance(text=json.dumps({"errcode": 0})))
        request = signin_request(url, 'post', data=req_data)

        response = self.viewset.as_view({'post': 'create'})(request)
        data = json.loads(response.content)
        assert data['data']['id']

        request = signin_request(url, 'get')

        response = self.viewset.as_view({'get': 'list'})(request)
        data = json.loads(response.content)
        assert data['data'][0]

        del_url = '{}/platform/{}/'.format(self.url, data['data'][0]['id'])
        request = signin_request(del_url, 'delete')
        response = self.viewset.as_view({'delete': 'destroy'})(
            request, pk=data['data'][0]['id'])
        data = json.loads(response.content)
        assert data['code'] == 200

        request = signin_request(url, 'get')
        response = self.viewset.as_view({'get': 'list'})(request)
        data = json.loads(response.content)
        assert len(data['data']) == 0
