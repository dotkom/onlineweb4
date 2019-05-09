from django.core import mail
from django.urls import reverse
from onlineweb4.fields.recaptcha import mock_validate_recaptcha
from rest_framework import status
from rest_framework.test import APITestCase

from apps.authentication.models import OnlineUser as User
from apps.authentication.models import RegisterToken


class SignupAPIURLTestCase(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.create_user_data = {
            'username': 'testuser133',
            'email': 'test33@example.org',
            'password': '12345678',
        }
        self.captcha_mock = {
            'recaptcha': '--captcha-mock--',
        }
        self.user_data_with_captcha = {
            **self.create_user_data,
            **self.captcha_mock,
        }

    def get_url(self, url):
        return self.client.get(reverse(url))

    def post_url(self, url, data={}):
        return self.client.post(reverse(url), data, **{
            'format': 'json', 'Content-Type': 'application/json'
        })

    def test_signup_http_get_returns_200(self):
        resp = self.get_url('users-list')

        self.assertEqual(status.HTTP_200_OK, resp.status_code)

    def test_signup_not_all_required_params_returns_400(self):
        resp = self.post_url('users-list')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, resp.status_code)

    @mock_validate_recaptcha()
    def test_signup_without_recaptcha_returns_400(self, _):

        resp = self.post_url('users-list', data=self.create_user_data)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, resp.status_code)

    @mock_validate_recaptcha()
    def test_signup_success_returns_201(self, _):
        resp = self.post_url('users-list', data=self.user_data_with_captcha)
        self.assertEqual(status.HTTP_201_CREATED, resp.status_code)

    @mock_validate_recaptcha()
    def test_signup_succuess_returns_correct_data(self, _):
        resp = self.post_url('users-list', data=self.user_data_with_captcha)

        self.assertEqual(status.HTTP_201_CREATED, resp.status_code)

        data = self.create_user_data
        created_user = resp.json()
        self.assertEqual(created_user['username'], data['username'])
        self.assertEqual(created_user['email'], data['email'])
        # Password should not be returned back to user
        self.assertEqual(created_user.get('password'), None)

    @mock_validate_recaptcha()
    def test_signup_twice_with_same_data_returns_400(self, _):
        self.post_url('users-list', data=self.user_data_with_captcha)
        resp_2 = self.post_url('users-list', data=self.user_data_with_captcha)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, resp_2.status_code)

    @mock_validate_recaptcha()
    def test_signup_twice_with_same_email_returns_400(self, _):
        first_user = self.user_data_with_captcha
        second_user = {
            **self.captcha_mock,
            'username': 'testuser456',
            'email': self.create_user_data.get('email'),
            'password': 'securepassword',
        }

        resp_1 = self.post_url('users-list', data=first_user)
        resp_2 = self.post_url('users-list', data=second_user)

        self.assertEqual(status.HTTP_201_CREATED, resp_1.status_code)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, resp_2.status_code)

    @mock_validate_recaptcha()
    def test_signup_twice_with_same_username_returns_400(self, _):
        first_user = self.user_data_with_captcha
        second_user = {
            **self.captcha_mock,
            'username': self.create_user_data.get('username'),
            'email': 'test44@example.org',
            'password': 'securepassword',
        }

        resp_1 = self.post_url('users-list', data=first_user)
        resp_2 = self.post_url('users-list', data=second_user)

        self.assertEqual(status.HTTP_201_CREATED, resp_1.status_code)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, resp_2.status_code)

    @mock_validate_recaptcha()
    def test_signup_success_sets_user_as_inactive(self, _):
        self.post_url('users-list', data=self.user_data_with_captcha)

        user = User.objects.get(username=self.create_user_data.get('username'))

        self.assertFalse(user.is_active)

    @mock_validate_recaptcha()
    def test_signup_success_sends_verification_email(self, _):
        self.post_url('users-list', data=self.user_data_with_captcha)

        self.assertEqual(mail.outbox[0].subject, 'Verifiser din konto')

    @mock_validate_recaptcha()
    def test_signup_success_verifcation_link_sets_user_as_active(self, _):
        self.post_url('users-list', data=self.user_data_with_captcha)

        register_token = RegisterToken.objects.get(email=self.create_user_data.get('email'))
        verify_url = reverse('auth_verify', args=[register_token.token])
        self.client.get(verify_url)

        user = User.objects.get(username=self.create_user_data.get('username'))
        self.assertTrue(user.is_active)
