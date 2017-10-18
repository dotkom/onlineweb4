from django.conf import settings
from django.test import TestCase, override_settings
from django_dynamic_fixture import G
from mock import patch

from apps.authentication.models import Email, OnlineUser
from apps.gsuite.mail_syncer.signals import (_get_error_message_from_httperror,
                                             insert_user_into_group_pass_if_already_member,
                                             remove_user_from_group_pass_if_not_subscribed)
from apps.gsuite.mail_syncer.tests.test_utils import create_http_error


class GSuiteSignalsTestCase(TestCase):
    def setUp(self):
        self.domain = settings.OW4_GSUITE_SYNC.get('DOMAIN')
        self.ow4_gsuite_sync = settings.OW4_GSUITE_SYNC

    def test_get_error_from_gsuite_http_error(self):
        error_message = "Member already exists"
        http_error = create_http_error(status=409, reason=error_message, error=error_message)
        parsed_error_message = _get_error_message_from_httperror(http_error)
        self.assertEqual(error_message, parsed_error_message)

    @patch('logging.Logger.warning')
    @patch('apps.gsuite.mail_syncer.signals.insert_email_into_g_suite_group')
    def test_insert_user_pass_if_already_in_group_passing(self, mocked_insert, mocked_logger):
        user = G(OnlineUser, infomail=False)
        email_addr = 'example@example.org'
        email = G(Email, email=email_addr, verified=True, primary=True)
        user.email_user.add(email)
        group_name = list(settings.OW4_GSUITE_SYNC.get('GROUPS').keys())[0]

        ow4_gsuite_sync = self.ow4_gsuite_sync.copy()
        ow4_gsuite_sync['ENABLE_INSERT'] = True

        error_message = 'Member already exists'
        mocked_insert.return_value = None
        mocked_insert.side_effect = create_http_error(status=409, reason=error_message, error=error_message)

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            insert_user_into_group_pass_if_already_member(self.domain, group_name, user.get_email().email)
            mocked_logger.assert_called_with(
                'Email address "{email}" was already subscribed to mailing list "{list}"!'.format(
                    email=email, list=group_name))

    @patch('logging.Logger.warning')
    @patch('apps.gsuite.mail_syncer.signals.remove_g_suite_user_from_group')
    def test_remove_user_from_group_pass_if_not_subscribed(self, mocked_remove, mocked_logger):
        user = G(OnlineUser, infomail=False)
        email_addr = 'example@example.org'
        email = G(Email, email=email_addr, verified=True, primary=True)
        user.email_user.add(email)
        group_name = list(settings.OW4_GSUITE_SYNC.get('GROUPS').keys())[0]

        ow4_gsuite_sync = self.ow4_gsuite_sync.copy()
        ow4_gsuite_sync['ENABLE_DELETE'] = True

        error_message = 'Resource Not Found'
        mocked_remove.return_value = None
        mocked_remove.side_effect = create_http_error(status=404, reason=error_message, error=error_message)

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            remove_user_from_group_pass_if_not_subscribed(self.domain, group_name, user.get_email().email)
            mocked_logger.assert_called_with(
                'Email address "{email}" was not subscribed to mailing list "{list}"!'.format(
                    email=email, list=group_name))
