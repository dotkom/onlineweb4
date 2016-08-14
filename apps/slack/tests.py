from unittest.mock import MagicMock, patch

from django.core.urlresolvers import reverse
from django.test import TestCase
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
            self.slack_invite.invite('invalid@email', 'Name')

    def test_invite_invalidName_raisesException(self):
        with self.assertRaises(SlackException):
            self.slack_invite.invite('valid@email.com', '')

    @patch('apps.slack.utils.requests.post')
    def test_invite_callsRequestsPost(self, post_mock):
        post_mock.side_effect = [
            MagicMock(status_code=200, json=lambda: {'ok': True})
        ]

        mail = "test@example.com"
        name = "Test"

        self.slack_invite.invite(mail, name)

        self.assertTrue(post_mock.called)

    @patch('apps.slack.utils.requests.post')
    def test_invite_statusCodeIsNot200_raisesException(self, post_mock):
        post_mock.side_effect = [
            MagicMock(status_code=403)
        ]

        with self.assertRaises(SlackException):
            self.slack_invite.invite("test@example.com", "Test")

    @patch('apps.slack.utils.requests.post')
    def test_invite_okIsNotTrue_raisesException(self, post_mock):
        post_mock.side_effect = [
            MagicMock(status_code=200, json=lambda: {'ok': False, 'error': 'Mocked!'})
        ]

        with self.assertRaises(SlackException):
            self.slack_invite.invite("test@example.com", "Test")

    @patch('apps.slack.utils.log.error')
    @patch('apps.slack.utils.requests.post')
    def test_invite_invalidAuth_logsError(self, post_mock, log_mock):
        post_mock.side_effect = [
            MagicMock(status_code=200, json=lambda: {'ok': False, 'error': 'invalid_auth'})
        ]

        with self.assertRaises(SlackException):
            self.slack_invite.invite("test@example.com", "Test")
        self.assertTrue(log_mock.called)


class InviteViewSetTest(APITestCase):
    @patch('apps.slack.views.SlackInvite')
    def test_post_withEmailAndName_returnsOk(self, slack_mock):
        url = reverse('slack-list')
        name = 'Test Testesen'
        email = 'test@example.com'

        response = self.client.post(url, {'name': name, 'email': email})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(slack_mock.called)

    @patch('apps.slack.views.SlackInvite')
    def test_post_withEmailOnly_fails(self, slack_mock):
        url = reverse('slack-list')
        email = 'test@example.com'

        response = self.client.post(url, {'email': email})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('apps.slack.views.SlackInvite')
    def test_post_withNameOnly_fails(self, slack_mock):
        url = reverse('slack-list')
        name = 'Willy Nickersen'

        response = self.client.post(url, {'name': name})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('apps.slack.views.SlackInvite.invite')
    def test_post_withSlackError_fails(self, slack_mock):
        slack_mock.side_effect = SlackException('Error')
        url = reverse('slack-list')
        name = 'Name'
        email = 'email@example.com'

        response = self.client.post(url, {'name': name, 'email': email})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(slack_mock.called)
