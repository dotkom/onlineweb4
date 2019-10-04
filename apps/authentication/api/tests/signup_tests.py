from django.core import mail
from django.urls import reverse
from django_dynamic_fixture import G
from onlineweb4.fields.recaptcha import mock_validate_recaptcha
from rest_framework import status

from apps.authentication.models import OnlineUser as User
from apps.authentication.models import RegisterToken
from apps.online_oidc_provider.test import OIDCTestCase


class SignupAPIURLTestCase(OIDCTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.password = '12345678'
        self.create_user_data = {
            'username': 'testuser133',
            'email': 'test33@example.org',
            'password': self.password,
        }
        self.captcha_mock = {
            'recaptcha': '--captcha-mock--',
        }
        self.user_data_with_captcha = {
            **self.create_user_data,
            **self.captcha_mock,
        }
        self.user: User = G(User, username='test_user')
        self.user.set_password(self.password)
        self.user.save()
        self.token = self.generate_access_token(self.user)
        self.headers = {
            **self.generate_headers(),
            **self.bare_headers,
        }

        self.url = reverse('users-list')
        self.id_url = lambda _id: reverse('users-detail', args=[_id])
        self.change_password_url = lambda _id: reverse('users-change-password', args=[_id])

    def test_signup_http_get_returns_200(self):
        response = self.client.get(self.url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_signup_not_all_required_params_returns_400(self):
        response = self.client.post(self.url, **self.bare_headers)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    @mock_validate_recaptcha()
    def test_signup_without_recaptcha_returns_400(self, _):
        response = self.client.post(self.url, data=self.create_user_data, **self.bare_headers)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    @mock_validate_recaptcha()
    def test_signup_success_returns_201(self, _):
        response = self.client.post(self.url, data=self.user_data_with_captcha, **self.bare_headers)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    @mock_validate_recaptcha()
    def test_signup_success_returns_correct_data(self, _):
        response = self.client.post(self.url, data=self.user_data_with_captcha, **self.bare_headers)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        data = self.create_user_data
        created_user = response.json()
        self.assertEqual(created_user['username'], data['username'])
        self.assertEqual(created_user['email'], data['email'])
        # Password should not be returned back to user
        self.assertEqual(created_user.get('password'), None)

    @mock_validate_recaptcha()
    def test_signup_twice_with_same_data_returns_400(self, _):
        self.client.post(self.url, data=self.user_data_with_captcha, **self.bare_headers)
        response = self.client.post(self.url, data=self.user_data_with_captcha, **self.bare_headers)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    @mock_validate_recaptcha()
    def test_signup_twice_with_same_email_returns_400(self, _):
        first_user = self.user_data_with_captcha
        second_user = {
            **self.captcha_mock,
            'username': 'testuser456',
            'email': self.create_user_data.get('email'),
            'password': 'securepassword',
        }

        response_1 = self.client.post(self.url, data=first_user, **self.bare_headers)
        response_2 = self.client.post(self.url, data=second_user, **self.bare_headers)

        self.assertEqual(status.HTTP_201_CREATED, response_1.status_code)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response_2.status_code)

    @mock_validate_recaptcha()
    def test_signup_twice_with_same_username_returns_400(self, _):
        first_user = self.user_data_with_captcha
        second_user = {
            **self.captcha_mock,
            'username': self.create_user_data.get('username'),
            'email': 'test44@example.org',
            'password': 'securepassword',
        }

        response_1 = self.client.post(self.url, data=first_user, **self.bare_headers)
        response_2 = self.client.post(self.url, data=second_user, **self.bare_headers)

        self.assertEqual(status.HTTP_201_CREATED, response_1.status_code)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response_2.status_code)

    @mock_validate_recaptcha()
    def test_signup_success_sets_user_as_inactive(self, _):
        self.client.post(self.url, data=self.user_data_with_captcha, **self.bare_headers)

        user = User.objects.get(username=self.create_user_data.get('username'))

        self.assertFalse(user.is_active)

    @mock_validate_recaptcha()
    def test_signup_password_checks_out(self, _):
        self.client.post(self.url, data=self.user_data_with_captcha, **self.bare_headers)

        user = User.objects.get(username=self.create_user_data.get('username'))

        self.assertNotEqual(user.password, self.password)
        self.assertTrue(user.check_password(self.password))

    @mock_validate_recaptcha()
    def test_signup_success_sends_verification_email(self, _):
        self.client.post(self.url, data=self.user_data_with_captcha, **self.bare_headers)

        self.assertEqual(mail.outbox[0].subject, 'Verifiser din konto')

    @mock_validate_recaptcha()
    def test_signup_success_verification_link_sets_user_as_active(self, _):
        self.client.post(self.url, data=self.user_data_with_captcha, **self.bare_headers)

        register_token = RegisterToken.objects.get(email=self.create_user_data.get('email'))
        verify_url = reverse('auth_verify', args=[register_token.token])
        self.client.get(verify_url)

        user = User.objects.get(username=self.create_user_data.get('username'))
        self.assertTrue(user.is_active)

    def test_user_update_their_name(self):
        new_first_name = 'Ola Kari'
        new_last_name = 'Nordmann'
        response = self.client.patch(self.id_url(self.user.id), {
            'first_name': new_first_name,
            'last_name': new_last_name,
        }, **self.headers)
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('first_name'), new_first_name)
        self.assertEqual(response.json().get('last_name'), new_last_name)

    def test_change_password(self):
        new_password = 'the_most_secure_password'
        response = self.client.put(self.change_password_url(self.user.id), {
            'current_password': self.password,
            'new_password': new_password,
            'new_password_retype': new_password,
        }, **self.headers)
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(self.user.check_password(new_password))

    def test_change_password_wrong_retype(self):
        new_password = 'the_most_secure_password'
        response = self.client.put(self.change_password_url(self.user.id), {
            'current_password': self.password,
            'new_password': new_password,
            'new_password_retype': 'some_random_shit',
        }, **self.headers)
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('non_field_errors'), ['Passordene stemmer ikke overens'])
        self.assertFalse(self.user.check_password(new_password))

    def test_change_password_wrong_current_password(self):
        new_password = 'the_most_secure_password'
        response = self.client.put(self.change_password_url(self.user.id), {
            'current_password': 'some_random_shit',
            'new_password': new_password,
            'new_password_retype': new_password,
        }, **self.headers)
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('current_password'), ['Nåværende passord stemmer ikke'])
        self.assertFalse(self.user.check_password(new_password))

    def test_change_password_new_password_missing(self):
        new_password = 'the_most_secure_password'
        response = self.client.put(self.change_password_url(self.user.id), {
            'current_password': self.password,
            'new_password_retype': new_password,
        }, **self.headers)
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('new_password'), ['Dette feltet er påkrevd.'])
        self.assertFalse(self.user.check_password(new_password))

    def test_change_password_new_password_invalid(self):
        new_password = '123'
        response = self.client.put(self.change_password_url(self.user.id), {
            'current_password': self.password,
            'new_password': new_password,
            'new_password_retype': new_password,
        }, **self.headers)
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('new_password'), ['Passordet er for kort. Det må bestå av minst 8 tegn.'])
        self.assertFalse(self.user.check_password(new_password))
