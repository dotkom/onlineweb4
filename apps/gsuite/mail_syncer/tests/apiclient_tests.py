import pytest
from django.conf import settings
from django.test import TestCase, override_settings
from django_dynamic_fixture import G
from googleapiclient.errors import HttpError
from mock import patch

from apps.authentication.models import OnlineUser
from apps.gsuite.mail_syncer.tests.test_utils import create_http_error
from apps.gsuite.mail_syncer.utils import (insert_email_into_g_suite_group,
                                           insert_ow4_user_into_g_suite_group,
                                           remove_g_suite_user_from_group)


class GSuiteAPITestCase(TestCase):
    def setUp(self):
        self.domain = settings.OW4_GSUITE_SYNC.get('DOMAIN')
        self.ow4_gsuite_sync = settings.OW4_GSUITE_SYNC.copy()

    @patch('logging.Logger.debug')
    def test_insert_when_insert_disabled(self, mocked_logger):
        group_name = list(settings.OW4_GSUITE_SYNC.get('GROUPS').keys())[0]
        email = 'example@example.org'

        ow4_gsuite_sync = self.ow4_gsuite_sync
        ow4_gsuite_sync['ENABLE_INSERT'] = False

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            resp = insert_email_into_g_suite_group(self.domain, group_name, email)
            self.assertIsNone(resp)
            mocked_logger.assert_called_with('Skipping inserting email "{email}" since ENABLE_INSERT is False.'.format(
                email=email))

    @patch('logging.Logger.debug')
    def test_remove_when_remove_disabled(self, mocked_logger):
        group_name = list(settings.OW4_GSUITE_SYNC.get('GROUPS').keys())[0]
        email = 'example@example.org'

        ow4_gsuite_sync = self.ow4_gsuite_sync
        ow4_gsuite_sync['ENABLE_DELETE'] = False

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            resp = remove_g_suite_user_from_group(self.domain, group_name, email)
            self.assertIsNone(resp)
            mocked_logger.assert_called_with('Skipping removing user "{user}" since ENABLE_DELETE is False.'.format(
                user=email))

    @patch('logging.Logger.debug')
    def test_remove_leader(self, mocked_logger):
        group_name = list(settings.OW4_GSUITE_SYNC.get('GROUPS').keys())[0]
        email = 'leder@{domain}'.format(domain=self.domain)

        ow4_gsuite_sync = self.ow4_gsuite_sync
        ow4_gsuite_sync['ENABLE_DELETE'] = False

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            resp = remove_g_suite_user_from_group(self.domain, group_name, email)
            self.assertIsNone(resp)
            mocked_logger.assert_called_with(
                'Skipping removing user "{user}" since (s)he should be on all lists.'.format(user=email))

    @patch('apps.gsuite.mail_syncer.utils.setup_g_suite_client', autospec=True)
    def test_insert_email_into_g_suite_group(self, mocked_g_suite_client):
        group_name = list(settings.OW4_GSUITE_SYNC.get('GROUPS').keys())[0]
        email = 'example@example.org'

        # Yes, really... https://stackoverflow.com/a/32956627
        mocked_g_suite_client.return_value.members.return_value.insert.return_value.execute.return_value = \
            {'email': email}

        ow4_gsuite_sync = self.ow4_gsuite_sync
        ow4_gsuite_sync['ENABLE_INSERT'] = True

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            resp = insert_email_into_g_suite_group(self.domain, group_name, email)
            self.assertEqual(resp.get('email'), email)

    @patch('apps.gsuite.mail_syncer.utils.setup_g_suite_client', autospec=True)
    def test_insert_email_into_g_suite_group_already_exists_raises(self, mocked_g_suite_client):
        group_name = list(settings.OW4_GSUITE_SYNC.get('GROUPS').keys())[0]
        email = 'example@example.org'

        error_reason = 'Member already exists'

        mocked_g_suite_client.return_value.members.return_value.insert.side_effect = \
            create_http_error(status=409, reason=error_reason, error=error_reason)

        ow4_gsuite_sync = self.ow4_gsuite_sync
        ow4_gsuite_sync['ENABLE_INSERT'] = True

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            with self.assertRaises(HttpError):
                insert_email_into_g_suite_group(self.domain, group_name, email)

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            insert_email_into_g_suite_group(self.domain, group_name, email, suppress_http_errors=True)

    @patch('apps.gsuite.mail_syncer.utils.insert_email_into_g_suite_group')
    def test_insert_ow4_user_into_g_suite_group(self, mocked_insert_ow4_user):
        group_name = list(settings.OW4_GSUITE_SYNC.get('GROUPS').keys())[0]
        user = G(OnlineUser, online_mail='example.address')

        mocked_insert_ow4_user.return_value = {'email': user.online_mail}

        ow4_gsuite_sync = self.ow4_gsuite_sync
        ow4_gsuite_sync['ENABLE_INSERT'] = True

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            resp = mocked_insert_ow4_user(self.domain, group_name, user)
            self.assertEqual(resp.get('email'), user.online_mail)

    @pytest.mark.skip  # We now create users if they don't exist.
    @patch('logging.Logger.error')
    @patch('apps.gsuite.mail_syncer.utils.setup_g_suite_client', autospec=True)
    def test_insert_ow4_user_into_g_suite_group_no_online_mail(self, mocked_gsuite_client, mocked_logger):
        group_name = list(settings.OW4_GSUITE_SYNC.get('GROUPS').keys())[0]
        user = G(OnlineUser, online_mail=None)

        ow4_gsuite_sync = self.ow4_gsuite_sync
        ow4_gsuite_sync['ENABLE_INSERT'] = True

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            insert_ow4_user_into_g_suite_group(self.domain, group_name, user)
            mocked_logger.assert_called_with(
                "OW4 User '{user}' ({user.pk}) missing Online email address! (current: '{user.online_mail}')".format(
                    user=user
                ), extra={'user': user, 'group': group_name})

    @patch('logging.Logger.debug')
    @patch('apps.gsuite.mail_syncer.utils.setup_g_suite_client', autospec=True)
    def test_remove_g_suite_user_from_g_suite_group_email_address(self, mocked_g_suite_client, mocked_logger):
        group_name = list(settings.OW4_GSUITE_SYNC.get('GROUPS').keys())[0]
        email = 'example@example.org'

        mocked_g_suite_client.return_value.members.return_value.delete.return_value.execute.return_value = \
            None

        ow4_gsuite_sync = self.ow4_gsuite_sync
        ow4_gsuite_sync['ENABLE_DELETE'] = True

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            resp = remove_g_suite_user_from_group(self.domain, group_name, email)
            self.assertIsNone(resp)
            mocked_logger.assert_called_with('Removal of user response: {resp}'.format(resp=resp))

    @patch('logging.Logger.debug')
    @patch('apps.gsuite.mail_syncer.utils.setup_g_suite_client', autospec=True)
    def test_remove_g_suite_user_from_g_suite_group_g_suite_dict(self, mocked_g_suite_client, mocked_logger):
        group_name = list(settings.OW4_GSUITE_SYNC.get('GROUPS').keys())[0]
        email = {'email': 'example@example.org'}

        mocked_g_suite_client.return_value.members.return_value.delete.return_value.execute.return_value = \
            None

        ow4_gsuite_sync = self.ow4_gsuite_sync
        ow4_gsuite_sync['ENABLE_DELETE'] = True

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            resp = remove_g_suite_user_from_group(self.domain, group_name, email)
            self.assertIsNone(resp)
            mocked_logger.assert_called_with('Removal of user response: {resp}'.format(resp=resp))

    @patch('logging.Logger.error')
    @patch('apps.gsuite.mail_syncer.utils.setup_g_suite_client', autospec=True)
    def test_remove_g_suite_user_from_g_suite_group_g_suite_dict_httperror(self, mocked_g_suite_client,
                                                                           mocked_logger):
        group_name = list(settings.OW4_GSUITE_SYNC.get('GROUPS').keys())[0]
        email = 'example@example.org'

        http_error = create_http_error(400, "Error", "Error")
        mocked_g_suite_client.return_value.members.return_value.delete.return_value.execute.side_effect = \
            http_error

        ow4_gsuite_sync = self.ow4_gsuite_sync
        ow4_gsuite_sync['ENABLED'] = True
        ow4_gsuite_sync['ENABLE_DELETE'] = True

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            self.assertRaises(HttpError, lambda: remove_g_suite_user_from_group(self.domain, group_name, email,
                                                                                suppress_http_errors=False))
        mocked_logger.assert_called_with('HttpError when deleting user "{user}" from G Suite group: {err}'.format(
            err=http_error, user=email), extra={'suppress_http_error': False})
