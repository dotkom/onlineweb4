import logging

from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from django_dynamic_fixture import G
from rest_framework import status
from rest_framework.test import APITestCase

from apps.authentication.constants import RoleType
from apps.authentication.models import GroupMember, GroupRole, OnlineGroup
from apps.authentication.models import OnlineUser as User
from apps.events.tests.utils import generate_user

logger = logging.getLogger(__name__)


class GroupRoleTestCase(APITestCase):
    def setUp(self):
        self.user: User = generate_user(username="test_user")
        self.user.is_superuser = True
        self.user.save()
        self.user.refresh_from_db()
        self.client.force_authenticate(user=self.user)
        self.other_user: User = generate_user(username="other_user")

        self.url = reverse("groups-list")
        self.id_url = lambda _id: self.url + str(_id) + "/"
        self.group_name = "Noenkom"
        self.group = G(Group, name=self.group_name)

    def test_roles_returns_200(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_200(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_group_by_id(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.id_url(self.group.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("id"), self.group.id)


class OnlineGroupTestCase(APITestCase):
    @staticmethod
    def create_group_roles():
        for role_type in RoleType.values:
            GroupRole.objects.create(role_type=role_type)

    @staticmethod
    def get_group_role(role_type: str) -> GroupRole:
        return GroupRole.objects.get(role_type=role_type)

    def _create_group(self, **kwargs) -> OnlineGroup:
        leader_role = self.get_group_role(RoleType.LEADER)
        deputy_leader_role = self.get_group_role(RoleType.DEPUTY_LEADER)
        group: OnlineGroup = G(OnlineGroup, **kwargs)
        group.admin_roles.add(leader_role)
        group.admin_roles.add(deputy_leader_role)
        return group

    def setUp(self):
        self.user: User = generate_user(username="test_user")
        self.user.is_superuser = True
        self.user.save()
        self.user.refresh_from_db()
        self.client.force_authenticate(user=self.user)
        self.other_user: User = generate_user(username="other_user")

        self.url = reverse("online_groups-list")
        self.id_url = lambda _id: self.url + str(_id) + "/"
        self.create_group_roles()

        self.group_name = "Noenkom"
        self.group_name_long = "Noenkomiteen"
        self.group = G(Group, name=self.group_name)
        self.group_data = {
            "group": self.group.id,
            "name_short": self.group_name,
            "name_long": self.group_name_long,
        }
        self.create_group = lambda: self._create_group(
            group=self.group, name_short=self.group_name, name_long=self.group_name_long
        )

    def test_groups_returns_200(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_200(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_superuser_can_create_groups(self):
        response = self.client.post(self.url, self.group_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_create_group_if_django_group_has_existing_online_group(self):
        self.create_group()

        response = self.client.post(self.url, self.group_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("group"),
            ["Denne Djangogruppen har allerede en Onlinegruppe"],
        )

    def test_cannot_create_online_group_without_django_group(self):
        wrong_group_id = -1
        response = self.client.post(
            self.url, {**self.group_data, "group": wrong_group_id}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get("group"),
            [f'Ugyldig pk "{wrong_group_id}" - objektet eksisterer ikke.'],
        )

    def test_regular_user_cannot_create_groups(self):
        self.user.is_superuser = False
        self.user.save()

        response = self.client.post(self.url, self.group_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_users_with_permission_can_create_groups(self):
        self.user.is_superuser = False
        self.user.save()
        permission = Permission.objects.get(codename="add_onlinegroup")
        self.user.user_permissions.add(permission)

        response = self.client.post(self.url, self.group_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_superuser_can_delete_group(self):
        online_group = self.create_group()

        response = self.client.delete(self.id_url(online_group.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_regular_user_cannot_delete_group(self):
        online_group = self.create_group()
        self.user.is_superuser = False
        self.user.save()

        response = self.client.delete(self.id_url(online_group.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_group_leader_can_delete_group(self):
        online_group = self.create_group()
        membership = GroupMember.objects.create(group=online_group, user=self.user)
        membership.roles.add(self.get_group_role(RoleType.LEADER))
        self.user.is_superuser = False
        self.user.save()

        response = self.client.delete(self.id_url(online_group.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_deputy_group_leader_can_delete_group(self):
        online_group = self.create_group()
        membership = GroupMember.objects.create(group=online_group, user=self.user)
        membership.roles.add(self.get_group_role(RoleType.LEADER))
        self.user.is_superuser = False
        self.user.save()

        response = self.client.delete(self.id_url(online_group.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
