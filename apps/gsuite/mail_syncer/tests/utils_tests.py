import pytest
from django.test import TestCase
from django_dynamic_fixture import G
from mock import patch

from apps.authentication.models import OnlineUser
from apps.gsuite.mail_syncer.utils import get_user
from apps.gsuite.utils import get_group_key, get_user_key


class GSuiteUtilsTestCase(TestCase):
    """Tests for simplifying parameter specifications to G Suite client"""
    def setUp(self):
        self.domain = 'example.org'
        self.group = 'dotkom'
        self.user = 'test'

    def test_get_group_key_no_params(self):
        self.assertRaises(ValueError, lambda: get_group_key('', ''))
        self.assertRaises(ValueError, lambda: get_group_key(self.domain, ''))
        self.assertRaises(ValueError, lambda: get_group_key('', self.group))

    def test_get_group_key(self):
        expected = '{group}@{domain}'.format(domain=self.domain, group=self.group)
        self.assertEqual(expected, get_group_key(self.domain, self.group))

    def test_get_group_key_returns_same_if_email(self):
        email = "{group}@{domain}".format(domain=self.domain, group=self.group)
        self.assertEqual(email, get_group_key(self.domain, email))

    def test_get_user_key_no_params(self):
        self.assertRaises(ValueError, lambda: get_user_key('', ''))
        self.assertRaises(ValueError, lambda: get_user_key(self.domain, ''))
        self.assertRaises(ValueError, lambda: get_user_key('', self.user))

    def test_get_user_key(self):
        expected = '{user}@{domain}'.format(domain=self.domain, user=self.user)
        self.assertEqual(expected, get_user_key(self.domain, self.user))

    def test_get_user_key_same_if_email(self):
        email = '{user}@{domain}'.format(domain=self.domain, user=self.user)
        self.assertEqual(email, get_user_key(self.domain, email))

    def test_get_user_no_params(self):
        self.assertRaises(ValueError, lambda: get_user(object))

    def test_get_user(self):
        user = G(OnlineUser)
        self.assertEqual(user, get_user(user, ow4=True))
        self.assertEqual(user.online_mail, get_user(user, gsuite=True))

        self.assertEqual(user, get_user(user.online_mail, ow4=True))
        self.assertEqual(user.online_mail, get_user(user.online_mail, gsuite=True))

    @pytest.mark.skip  # We now create users if they don't exist.
    @patch('logging.Logger.warning')
    def test_get_onlineuser_not_exist(self, mocked_logger):
        email = '{user}@{domain}'.format(domain=self.domain, user=self.user)
        self.assertRaises(OnlineUser.DoesNotExist, lambda: get_user(email, ow4=True))
        mocked_logger.assert_called_with('User "{user}" does not exist on OW4!'.format(user=email))
