import logging
from copy import deepcopy
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django_dynamic_fixture import G
from rest_framework import status

from apps.authentication.constants import GroupType, RoleType
from apps.authentication.models import (
    Email,
    GroupRole,
    OnlineGroup,
    OnlineUser,
    RegisterToken,
)
from apps.authentication.validators import validate_rfid


class AuthenticationTest(TestCase):
    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.user = G(OnlineUser, username="testuser")
        self.now = timezone.now()

    def testTokenActive(self):
        self.logger.debug("Testing that the token is active, with dynamic fixtures")
        self.registertoken = G(RegisterToken, created=self.now)
        self.assertTrue(self.registertoken.is_valid)

    def testTokenNotActive(self):
        self.logger.debug("Testing that the token is not active, with dynamic fixtures")
        self.registertoken = G(RegisterToken, created=self.now - timedelta(days=1))
        self.assertFalse(self.registertoken.is_valid)

    def testYearZeroIfNoFieldOfStudy(self):
        self.user.started_date = self.now.date()
        self.assertEqual(0, self.user.year)

    def testYearOneBachelor(self):
        self.user.started_date = self.now.date()
        self.user.field_of_study = 1
        self.assertEqual(1, self.user.year)

    def testYearTwoBachelor(self):
        self.user.started_date = self.now.date() - timedelta(days=365)
        self.user.field_of_study = 1
        self.assertEqual(2, self.user.year)

    def testYearThreeBachelor(self):
        self.user.started_date = self.now.date() - timedelta(days=365 * 2)
        self.user.field_of_study = 1
        self.assertEqual(3, self.user.year)

    def testYearFourBachelorShouldNotBePossible(self):
        self.user.started_date = self.now.date() - timedelta(days=365 * 3)
        self.user.field_of_study = 1
        self.assertEqual(3, self.user.year)

    def testYearFourMaster(self):
        self.user.started_date = self.now.date()
        self.user.field_of_study = 10
        self.assertEqual(4, self.user.year)

    def testYearFiveMaster(self):
        self.user.started_date = self.now.date() - timedelta(days=365)
        self.user.field_of_study = 10
        self.assertEqual(5, self.user.year)

    def testYearSixMasterShouldNotBePossible(self):
        self.user.started_date = self.now.date() - timedelta(days=365 * 2)
        self.user.field_of_study = 10
        self.assertEqual(5, self.user.year)

    def testFieldOfStudy30IsAlsoMaster(self):
        self.user.started_date = self.now.date()
        self.user.field_of_study = 30
        self.assertEqual(4, self.user.year)

    def testPhD(self):
        self.user.started_date = self.now.date()
        self.user.field_of_study = 80
        self.assertEqual(6, self.user.year)

    def testPhdYearCouldBeInfinite(self):
        self.user.started_date = self.now.date() - timedelta(days=365 * 5)
        self.user.field_of_study = 80
        self.assertEqual(11, self.user.year)

    def testInternational(self):
        self.user.started_date = self.now.date()
        self.user.field_of_study = 90
        self.assertEqual(1, self.user.year)

    def testSocial(self):
        self.user.started_date = self.now.date()
        self.user.field_of_study = 40
        self.assertEqual(0, self.user.year)

    def testSocialYearIncrementShouldNotBePossible(self):
        self.user.started_date = self.now.date() - timedelta(days=365)
        self.user.field_of_study = 40
        self.assertEqual(0, self.user.year)

    def testEmailPrimaryOnCreation(self):
        email = G(Email, user=self.user, email="test@test.com")
        self.assertTrue(email.primary)


class UserGroupSyncTestCase(TestCase):
    def setUp(self):
        self.user = G(OnlineUser)
        self.source_group = G(Group)
        self.destination_group = G(Group)

        group_syncer_settings = deepcopy(settings)
        self.GROUP_SYNCER_SETTINGS = [
            {
                "name": "Group syncer test",
                "source": [self.source_group.id],
                "destination": [self.destination_group.id],
            }
        ]

        group_syncer_settings.GROUP_SYNCER = self.GROUP_SYNCER_SETTINGS

        self.group_syncer_settings = group_syncer_settings

    def test_dont_sync_members_if_no_syncers(self):
        self.user.groups.add(self.source_group)

        self.assertNotIn(self.destination_group, self.user.groups.all())

    def test_sync_members_of_group_to_group(self):
        with override_settings(GROUP_SYNCER=self.GROUP_SYNCER_SETTINGS):
            self.user.groups.add(self.source_group)

        self.assertIn(self.destination_group, self.user.groups.all())

    def test_sync_remove_user_from_group(self):
        with override_settings(GROUP_SYNCER=self.GROUP_SYNCER_SETTINGS):
            self.user.groups.add(self.source_group)
            self.user.groups.remove(self.source_group)

        self.assertNotIn(self.destination_group, self.user.groups.all())


class AuthenticationURLTestCase(TestCase):
    def test_auth_login_view(self):
        url = reverse("auth_login")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auth_register_view(self):
        url = reverse("auth_register")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auth_recover_view(self):
        url = reverse("auth_recover")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RfidValidatorTestCase(TestCase):
    def test_valid_8_char_rfid_passes_test(self):
        # Validation failure raises exception, we test this by expecting it not to raise an exception.
        validate_rfid("12345678")

    def test_valid_10_char_rfid_passes_test(self):
        # Validation failure raises exception, we test this by expecting it not to raise an exception.
        validate_rfid("1234567890")

    def test_invalid_rfid_fails_test(self):
        self.assertRaises(ValidationError, lambda: validate_rfid("1234567"))
        self.assertRaises(ValidationError, lambda: validate_rfid("abcdefgh"))
        self.assertRaises(ValidationError, lambda: validate_rfid("abcdefghij"))
        self.assertRaises(ValidationError, lambda: validate_rfid("        "))
        self.assertRaises(ValidationError, lambda: validate_rfid("          "))


class GroupPermissionTestCase(TestCase):
    def setUp(self):
        django_group = G(Group)
        self.group = OnlineGroup.objects.create(
            group=django_group,
            name_short="Testkom",
            name_long="Testkomiteen",
            group_type=GroupType.COMMITTEE,
        )
        self.user1: OnlineUser = G(OnlineUser)
        self.member1 = self.group.add_user(self.user1)

        self.user2: OnlineUser = G(OnlineUser)
        self.member2 = self.group.add_user(self.user2)

        self.user3: OnlineUser = G(OnlineUser)
        self.member3 = self.group.add_user(self.user3)

        self.test_perm = "authentication.change_onlinegroup"

    def get_role(self, role: str):
        return GroupRole.get_for_type(role)

    def test_leader_gets_permission(self):
        self.member1.roles.add(self.get_role(RoleType.LEADER))

        # User 1 is a leader, user 2 is regular member
        self.assertTrue(self.user1.has_perm(self.test_perm, self.group))
        self.assertFalse(self.user2.has_perm(self.test_perm, self.group))

        # Switch up the roles, to see if permissions are added and removed as they should
        self.member1.roles.remove(self.get_role(RoleType.LEADER))
        self.member2.roles.add(self.get_role(RoleType.DEPUTY_LEADER))

        # user 1 permissions should be revoked, while user 2 get permission for being deputy leader
        self.assertFalse(self.user1.has_perm(self.test_perm, self.group))
        self.assertTrue(self.user2.has_perm(self.test_perm, self.group))

    def test_permissions_propagate_from_parent_groups(self):
        parent_group: OnlineGroup = G(OnlineGroup, group=G(Group))
        user: OnlineUser = G(OnlineUser)
        member = parent_group.add_user(user)
        member.roles.add(self.get_role(RoleType.LEADER))

        self.group.parent_group = parent_group
        self.group.save()

        self.assertTrue(user.has_perm(self.test_perm, self.group))

        # Test when the role is added after the group is set as the parent
        user: OnlineUser = G(OnlineUser)
        member = parent_group.add_user(user)
        member.roles.add(self.get_role(RoleType.LEADER))

        self.assertTrue(user.has_perm(self.test_perm, self.group))

        sub_group: OnlineGroup = G(OnlineGroup, group=G(Group))
        sub_group.parent_group = self.group
        sub_group.save()

        self.assertTrue(user.has_perm(self.test_perm, sub_group))
