from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from mock import patch

from apps.gsuite.auth import build_g_suite_service
from apps.gsuite.mail_syncer.utils import setup_g_suite_client


class GSuiteAPIClientTestCase(TestCase):
    def setUp(self):
        self.ow4_gsuite_settings = settings.OW4_GSUITE_SETTINGS.copy()

    def test_build_gsuite_api_client_no_credentials(self):
        self.assertRaises(
            ValueError, lambda: build_g_suite_service("admin", "directory_v1", None)
        )

    def test_build_gsuite_api_client_not_enabled(self):
        self.ow4_gsuite_settings["ENABLED"] = False
        with override_settings(OW4_GSUITE_SETTINGS=self.ow4_gsuite_settings):
            self.assertRaises(
                ImproperlyConfigured,
                lambda: build_g_suite_service("admin", "directory_v1", "some"),
            )

    @patch("apps.gsuite.mail_syncer.utils.build_and_authenticate_g_suite_service")
    @patch("logging.Logger.error")
    def test_setup_g_suite_client_no_delegated_account(
        self, mocked_logger, mocked_return_func
    ):
        ow4_gsuite_sync = settings.OW4_GSUITE_SYNC.copy()
        ow4_gsuite_sync["ENABLED"] = True
        self.ow4_gsuite_settings["ENABLED"] = True
        self.ow4_gsuite_settings["DELEGATED_ACCOUNT"] = None
        mocked_return_func.return_value = None
        with override_settings(
            OW4_GSUITE_SETTINGS=self.ow4_gsuite_settings,
            OW4_GSUITE_SYNC=ow4_gsuite_sync,
        ):
            setup_g_suite_client()
            mocked_logger.assert_called_with(
                "To be able to actually execute calls towards G Suite you must define "
                "DELEGATED_ACCOUNT."
            )

    @patch("apps.gsuite.mail_syncer.utils.build_and_authenticate_g_suite_service")
    @patch("logging.Logger.warning")
    def test_setup_g_suite_client_no_unsafe_enabled(
        self, mocked_logger, mocked_return_func
    ):
        ow4_gsuite_sync = settings.OW4_GSUITE_SYNC.copy()
        self.ow4_gsuite_settings["ENABLED"] = True
        ow4_gsuite_sync["ENABLED"] = True
        ow4_gsuite_sync["ENABLE_INSERT"] = False
        ow4_gsuite_sync["ENABLE_DELETE"] = False
        mocked_return_func.return_value = None
        with override_settings(
            OW4_GSUITE_SETTINGS=self.ow4_gsuite_settings,
            OW4_GSUITE_SYNC=ow4_gsuite_sync,
        ):
            setup_g_suite_client()
            mocked_logger.assert_called_with(
                "To be able to execute unsafe calls towards G Suite you must allow this "
                "in settings."
                'Neither "ENABLE_INSERT" nor "ENABLE_DELETE" are enabled.'
            )
