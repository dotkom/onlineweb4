from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class SignupAPIURLTestCase(APITestCase):
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

    def test_signup_success_returns_201(self):
        data = {
            'username': 'testuser133',
            'email': 'test33@example.org',
            'password': '12345678',
        }

        resp = self.post_url('users-list', data=data)

        self.assertEqual(status.HTTP_201_CREATED, resp.status_code)
