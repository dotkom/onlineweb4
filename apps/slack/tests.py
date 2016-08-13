from django.test import TestCase
from unittest.mock import MagicMock, patch

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

    @patch('apps.slack.utils.requests.post')
    def test_invite_callsRequestsPost(self, post_mock):
        post_mock.side_effect = [
            MagicMock(status_code=200, data={'ok': True})
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
    def test_invite_statusCodeIsNot200_raisesException(self, post_mock):
        post_mock.side_effect = [
            MagicMock(status_code=200, data={'ok': False, 'error': 'Mocked!'})
        ]

        with self.assertRaises(SlackException):
            self.slack_invite.invite("test@example.com", "Test")
