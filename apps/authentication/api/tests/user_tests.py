from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class SignupAPIURLTestCase(APITestCase):
    def request_url(self, url):
        return self.client.get(reverse(url))

    def test_get_users_list_returns_200(self):
        response = self.request_url('users-list')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
