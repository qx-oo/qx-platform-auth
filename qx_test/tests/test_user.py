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
    def test_signup(self, rf, mocker, user_data_init):
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

        url = '{}/user/signup-platform/'.format(self.url)

        req_data = {
            "openid": "test_openid",
            "mobile": '18866668800',
            "password": "12345678",
            'platform': 'wechat',
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
        breakpoint()
        # assert not data['data']['is_register']


# class TestPlatformViewSet:

#     def test_bind(self):
#         pass

    # @pytest.mark.django_db
    # def test_signin(self, rf, user_data_init):
    #     url = '{}/user/signin/'.format(self.url)

    #     data = {
    #         "account": "18866668888",
    #         "password": "12345678"
    #     }
    #     request = rf.post(
    #         url, data=data,
    #         content_type='application/json')
    #     response = self.viewset.as_view({'post': 'signin'})(request)
    #     assert response.status_code == 200
    #     data = json.loads(response.content)
    #     assert data['data']['token']

    #     _, code = CodeMsg('18866668888',
    #                       _type='signin').get_new_code()
    #     data = {
    #         "account": "18866668888",
    #         "code": code
    #     }
    #     request = rf.post(
    #         url, data=data,
    #         content_type='application/json')
    #     response = self.viewset.as_view({'post': 'signin'})(request)
    #     assert response.status_code == 200
    #     data = json.loads(response.content)
    #     assert data['data']['token']

    # @pytest.mark.django_db
    # def test_signup(self, rf, user_data_init):
    #     mobile = '18866668800'
    #     _, code = CodeMsg(mobile,
    #                       _type='signup').get_new_code()

    #     url = '{}/user/signup/'.format(self.url)

    #     data = {
    #         "mobile": mobile,
    #         "password": "12345678",
    #         "code": code,
    #         "userinfo": {
    #             "name": "test_user",
    #             "age": 15,
    #         }
    #     }
    #     request = rf.post(
    #         url, data=data,
    #         content_type='application/json')
    #     response = self.viewset.as_view({'post': 'signup'})(request)
    #     assert response.status_code == 200
    #     data = json.loads(response.content)
    #     assert data['data']['token']

    # @pytest.mark.django_db
    # def test_account_exists(self, rf, user_data_init):

    #     url = '{}/user/account-exists/?account={}'.format(
    #         self.url, '18866668880')

    #     request = rf.get(url)
    #     response = self.viewset.as_view({'get': 'account_exists'})(request)
    #     assert response.status_code == 200
    #     data = json.loads(response.content)
    #     assert data['data']['exists']
