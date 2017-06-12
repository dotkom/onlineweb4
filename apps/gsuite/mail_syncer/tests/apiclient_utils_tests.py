from django.conf import settings
from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from django_dynamic_fixture import G
from googleapiclient.errors import HttpError
from mock import patch

from apps.authentication.models import OnlineUser
from apps.gsuite.mail_syncer.tests.test_utils import create_http_error
from apps.gsuite.mail_syncer.utils import (_get_excess_users_in_g_suite,
                                           _get_g_suite_user_from_g_suite_user_list,
                                           _get_missing_ow4_users_for_g_suite,
                                           check_amount_of_members_ow4_g_suite,
                                           get_appropriate_g_suite_group_names_for_user,
                                           get_excess_groups_for_user, get_g_suite_groups_for_user,
                                           get_g_suite_users_for_group,
                                           get_missing_g_suite_group_names_for_user,
                                           get_ow4_users_for_group, insert_email_into_g_suite_group,
                                           insert_ow4_user_into_g_suite_group)


class GSuiteAPIUtilsTestCase(TestCase):
    """Tests for ow4-side utils of G Suite app, like "get excess groups for user"."""
    def setUp(self):
        self.domain = 'example.org'
        self.group = 'dotkom'

    @patch('logging.Logger.info')
    @patch('apps.gsuite.mail_syncer.utils.setup_g_suite_client', autospec=True)
    def test_insert_ow4_user_into_g_suite_group(self, mocked_insert, mocked_logger):
        user = G(OnlineUser, online_mail='firstname.lastname')
        group_email = self.group + '@' + self.domain

        ow4_gsuite_sync = settings.OW4_GSUITE_SYNC
        ow4_gsuite_sync['ENABLED'] = True
        ow4_gsuite_sync['ENABLE_INSERT'] = True

        mocked_insert.return_value.members.return_value.insert.return_value.execute.return_value = \
            {'email': user.online_mail}

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            resp = insert_email_into_g_suite_group(self.domain, self.group, user.online_mail)
            self.assertEqual(user.online_mail, resp.get('email'))

        mocked_logger.assert_called_with(
            "Inserting '{user}' into G Suite group '{group}'.".format(user=user.online_mail, group=group_email),
            extra={'email': user.online_mail, 'group': group_email})

    @patch('logging.Logger.error')
    def test_insert_ow4_user_into_g_suite_group_no_online_mail(self, mocked_logger):
        user = G(OnlineUser, online_mail=None)
        insert_ow4_user_into_g_suite_group(self.domain, self.group, user)
        mocked_logger.assert_called_with("OW4 User '{user}' ({user.pk}) missing Online email address! "
                                         "(current: '{user.online_mail}')".format(user=user),
                                         extra={'user': user, 'group': self.group})

    def test_get_ow4_users_for_group(self):
        group = G(Group)
        user1 = G(OnlineUser)
        user2 = G(OnlineUser)
        user3 = G(OnlineUser)

        ow4_gsuite_sync = settings.OW4_GSUITE_SYNC
        ow4_gsuite_sync['ENABLED'] = False

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            group.user_set.add(user1, user2, user3)

        resp = get_ow4_users_for_group(group.name)
        self.assertIn(user1, resp)
        self.assertIn(user2, resp)
        self.assertIn(user3, resp)

    def test_get_appropriate_g_suite_group_names_for_user(self):
        user = G(OnlineUser)
        G(Group, name='appkom')
        dotkom = G(Group, name='dotkom')

        ow4_gsuite_sync = settings.OW4_GSUITE_SYNC
        ow4_gsuite_sync['ENABLED'] = False
        ow4_gsuite_sync['GROUPS'] = {'appkom': 'appkom', 'dotkom': 'dotkom'}

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            dotkom.user_set.add(user)
            groups = get_appropriate_g_suite_group_names_for_user(self.domain, user)

        self.assertEqual(1, len(groups))
        self.assertIn(dotkom.name.lower(), groups)

    def test_check_amount_of_members_equal(self):
        g_suite_members = [{'email': 'test@example.org'}]
        user = G(OnlineUser)
        group = G(Group, name='dotkom')

        ow4_gsuite_sync = settings.OW4_GSUITE_SYNC
        ow4_gsuite_sync['ENABLED'] = False
        ow4_gsuite_sync['GROUPS'] = {'appkom': 'appkom', 'dotkom': 'dotkom'}

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            group.user_set.add(user)

        self.assertTrue(check_amount_of_members_ow4_g_suite(g_suite_members, group.user_set.all(), quiet=False))

    @patch('logging.Logger.debug')
    def test_check_amount_of_members_ow4_dominates(self, mocked_logger):
        g_suite_members = [{'email': 'test@example.org'}]
        user = G(OnlineUser)
        user2 = G(OnlineUser)
        group = G(Group, name='dotkom')

        ow4_gsuite_sync = settings.OW4_GSUITE_SYNC
        ow4_gsuite_sync['ENABLED'] = False
        ow4_gsuite_sync['GROUPS'] = {'appkom': 'appkom', 'dotkom': 'dotkom'}

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            group.user_set.add(user)
            group.user_set.add(user2)

        self.assertFalse(check_amount_of_members_ow4_g_suite(g_suite_members, group.user_set.all(), quiet=False))
        mocked_logger.assert_called_with('There are more users on OW4 ({ow4_count}) than in G Suite ({g_suite_count}). '
                                         'Need to update G Suite with new members.'.format(
                                             g_suite_count=len(g_suite_members), ow4_count=group.user_set.count()))

    @patch('logging.Logger.debug')
    def test_check_amount_of_members_gsuite_dominates(self, mocked_logger):
        g_suite_members = [{'email': 'test@example.org'}, {'email': 'test2@example.org'}]
        user = G(OnlineUser)
        group = G(Group, name='dotkom')

        ow4_gsuite_sync = settings.OW4_GSUITE_SYNC
        ow4_gsuite_sync['ENABLED'] = False
        ow4_gsuite_sync['GROUPS'] = {'appkom': 'appkom', 'dotkom': 'dotkom'}

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            group.user_set.add(user)

        self.assertFalse(check_amount_of_members_ow4_g_suite(g_suite_members, group.user_set.all(), quiet=False))
        mocked_logger.assert_called_with('There are more users in G Suite ({g_suite_count}) than on OW4 ({ow4_count}). '
                                         'Need to trim inactive users from G Suite.'.format(
                                             g_suite_count=len(g_suite_members), ow4_count=group.user_set.count()))

    def test_get_excess_users_in_gsuite(self):
        g_suite_members = [{'email': 'test@example.org'}, {'email': 'test2@example.org'}]
        user = G(OnlineUser, online_mail='test')
        G(OnlineUser, online_mail='test2')
        group = G(Group, name='dotkom')

        ow4_gsuite_sync = settings.OW4_GSUITE_SYNC
        ow4_gsuite_sync['ENABLED'] = False
        ow4_gsuite_sync['GROUPS'] = {'appkom': 'appkom', 'dotkom': 'dotkom'}

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            group.user_set.add(user)
            users = _get_excess_users_in_g_suite(g_suite_members, group.user_set.all())

        self.assertIn({'email': 'test2@example.org'}, users)

    def test_g_suite_user_from_g_suite_user_list(self):
        user = {'email': 'test@example.org'}
        g_suite_members = [user, {'email': 'test2@example.org'}]

        resp = _get_g_suite_user_from_g_suite_user_list(g_suite_members, user.get('email'))
        self.assertEqual(user, resp)

    def test_get_missing_ow4_users_for_g_suite(self):
        g_suite_members = [{'email': 'test@%s' % self.domain}]
        user = G(OnlineUser, online_mail='test')
        user2 = G(OnlineUser, online_mail='test2')
        group = G(Group, name='dotkom')

        ow4_gsuite_sync = settings.OW4_GSUITE_SYNC
        ow4_gsuite_sync['DOMAIN'] = self.domain
        ow4_gsuite_sync['ENABLED'] = False
        ow4_gsuite_sync['GROUPS'] = {'appkom': 'appkom', 'dotkom': 'dotkom'}

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            group.user_set.add(user, user2)
            users = _get_missing_ow4_users_for_g_suite(g_suite_members, group.user_set.all())

        self.assertIn(user2, users)

    @patch('apps.gsuite.mail_syncer.utils.get_g_suite_groups_for_user')
    def test_get_missing_g_suite_group_names_for_user(self, mocked_client):
        user = G(OnlineUser)
        dotkom = G(Group, name='dotkom')

        ow4_gsuite_sync = settings.OW4_GSUITE_SYNC
        ow4_gsuite_sync['ENABLED'] = False
        ow4_gsuite_sync['GROUPS'] = {'appkom': 'appkom', 'dotkom': 'dotkom'}

        mocked_client.return_value = [{'name': 'dotkom@' + self.domain}]

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            dotkom.user_set.add(user)
            groups = get_missing_g_suite_group_names_for_user(self.domain, user)

        self.assertEqual(1, len(groups))
        self.assertIn(dotkom.name.lower(), groups)

    @patch('apps.gsuite.mail_syncer.utils.get_g_suite_groups_for_user')
    def test_get_excess_groups_for_user(self, mocked_client):
        user = G(OnlineUser)
        dotkom = G(Group, name='dotkom')

        ow4_gsuite_sync = settings.OW4_GSUITE_SYNC
        ow4_gsuite_sync['ENABLED'] = False
        ow4_gsuite_sync['GROUPS'] = {'appkom': 'appkom', 'dotkom': 'dotkom'}

        mocked_client.return_value = [{'name': 'dotkom'}]

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            groups = get_excess_groups_for_user(self.domain, user)

        self.assertEqual(1, len(groups))
        self.assertIn(dotkom.name.lower(), groups)

    @patch('apps.gsuite.mail_syncer.utils.setup_g_suite_client', autospec=True)
    def test_get_g_suite_users_for_group(self, mocked_g_suite_client):
        ow4_gsuite_sync = settings.OW4_GSUITE_SYNC
        ow4_gsuite_sync['ENABLED'] = True

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            mocked_g_suite_client.return_value.members.return_value.list.return_value.execute.return_value.\
                get.return_value = [{'email': '1@' + self.domain}]
            resp = get_g_suite_users_for_group(self.domain, self.group, suppress_http_errors=True)
            self.assertEqual(1, len(resp))

            http_error = create_http_error(400, "Error", "Error")
            mocked_g_suite_client.return_value.members.return_value.list.return_value.execute.return_value. \
                get.side_effect = http_error
            self.assertRaises(HttpError, lambda: get_g_suite_users_for_group(self.domain, self.group))

    @patch('apps.gsuite.mail_syncer.utils.setup_g_suite_client', autospec=True)
    def test_get_g_suite_users_for_group_no_members(self, mocked_g_suite_client):
        ow4_gsuite_sync = settings.OW4_GSUITE_SYNC
        ow4_gsuite_sync['ENABLED'] = True

        mocked_g_suite_client.return_value.members.return_value.list.return_value.execute.return_value. \
            get.return_value = None

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            resp = get_g_suite_users_for_group(self.domain, self.group)
            self.assertEqual(0, len(resp))

    @patch('apps.gsuite.mail_syncer.utils.setup_g_suite_client', autospec=True)
    def test_get_g_suite_groups_for_user(self, mocked_g_suite_client):
        user = G(OnlineUser)

        ow4_gsuite_sync = settings.OW4_GSUITE_SYNC
        ow4_gsuite_sync['ENABLED'] = True

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            mocked_g_suite_client.return_value.groups.return_value.list.return_value.execute.return_value. \
                get.return_value = [{'name': 'dotkom@' + self.domain}]
            resp = get_g_suite_groups_for_user(self.domain, user, suppress_http_errors=True)
            self.assertEqual(1, len(resp))

            http_error = create_http_error(400, "Error", "Error")
            mocked_g_suite_client.return_value.groups.return_value.list.return_value.execute.return_value. \
                get.side_effect = http_error
            self.assertRaises(HttpError, lambda: get_g_suite_groups_for_user(self.domain, user))

    @patch('apps.gsuite.mail_syncer.utils.setup_g_suite_client', autospec=True)
    def test_get_g_suite_groups_for_user_no_members(self, mocked_g_suite_client):
        user = G(OnlineUser)

        ow4_gsuite_sync = settings.OW4_GSUITE_SYNC
        ow4_gsuite_sync['ENABLED'] = True

        mocked_g_suite_client.return_value.groups.return_value.list.return_value.execute.return_value. \
            get.return_value = None

        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            resp = get_g_suite_groups_for_user(self.domain, user)
            self.assertEqual(0, len(resp))
