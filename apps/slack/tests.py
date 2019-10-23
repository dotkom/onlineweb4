from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.slack.utils import SlackException, SlackInvite


class SlackInviteTest(TestCase):
    def setUp(self):
        self.slack_invite = SlackInvite()

    def test_url_returns_string(self):
        self.assertIsInstance(self.slack_invite._url(), str)

    def test_match_email_invalidEmail_returnsFalse(self):
        self.assertFalse(self.slack_invite._match_email('mail.example'))
        self.assertFalse(self.slack_invite._match_email('mail@example.'))
        self.assertFalse(self.slack_invite._match_email('@example.com'))
        self.assertTrue(self.slack_invite._match_email('mail@example.com'))

    def test_invite_matchEmailFails_raisesException(self):
        with self.assertRaises(SlackException):
            self.slack_invite.invite('invalid@email')

    @patch('apps.slack.utils.requests.post')
    def test_invite_callsRequestsPost(self, post_mock):
        post_mock.side_effect = [
            MagicMock(status_code=200, json=lambda: {'ok': True})
        ]
        mail = "test@example.com"

        self.slack_invite.invite(mail)

        self.assertTrue(post_mock.called)

    @patch('apps.slack.utils.requests.post')
    def test_invite_statusCodeIsNot200_raisesException(self, post_mock):
        post_mock.side_effect = [
            MagicMock(status_code=403)
        ]

        with self.assertRaises(SlackException):
            self.slack_invite.invite("test@example.com")

    @patch('apps.slack.utils.requests.post')
    def test_invite_okIsNotTrue_raisesException(self, post_mock):
        post_mock.side_effect = [
            MagicMock(status_code=200, json=lambda: {'ok': False, 'error': 'Mocked!'})
        ]

        with self.assertRaises(SlackException):
            self.slack_invite.invite("test@example.com")

    @patch('apps.slack.utils.log.error')
    @patch('apps.slack.utils.requests.post')
    def test_invite_invalidAuth_logsError(self, post_mock, log_mock):
        post_mock.side_effect = [
            MagicMock(status_code=200, json=lambda: {'ok': False, 'error': 'invalid_auth'})
        ]

        with self.assertRaises(SlackException):
            self.slack_invite.invite('test@example.com')
        self.assertTrue(log_mock.called)


class InviteViewSetTest(APITestCase):
    @patch('apps.slack.views.SlackInvite')
    def test_post_withEmail_returnsOk(self, slack_mock):
        url = reverse('slack-list')
        email = 'test@example.com'

        response = self.client.post(url, {'email': email})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(slack_mock.called)

    @patch('apps.slack.views.SlackInvite.invite')
    def test_post_withSlackError_fails(self, slack_mock):
        slack_mock.side_effect = SlackException('Error')
        url = reverse('slack-list')
        email = 'email@example.com'

        response = self.client.post(url, {'email': email})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(slack_mock.called)
