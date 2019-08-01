from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from django_dynamic_fixture import G
from rest_framework import status

from apps.authentication.constants import RoleType
from apps.authentication.models import GroupMember, GroupRole, OnlineGroup
from apps.authentication.models import OnlineUser as User
from apps.events.tests.utils import generate_user
from apps.oidc_provider.test import OIDCTestCase


class GroupRoleTestCase(OIDCTestCase):

    def setUp(self):
        self.user: User = generate_user(username='test_user')
        self.user.is_superuser = True
        self.user.save()
        self.user.refresh_from_db()
        self.other_user: User = generate_user(username='other_user')
        self.token = self.generate_access_token(self.user)
        self.headers = {
            **self.generate_headers(),
            **self.bare_headers,
        }

        self.url = reverse('groups-list')
        self.id_url = lambda _id: self.url + str(_id) + '/'
        self.group_name = 'Noenkom'
        self.group = G(Group, name=self.group_name)

    def test_roles_returns_200(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_200(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_group_by_id(self):
        response = self.client.get(self.id_url(self.group.id), **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('id'), self.group.id)


class OnlineGroupTestCase(OIDCTestCase):

    def setUp(self):
        self.user: User = generate_user(username='test_user')
        self.user.is_superuser = True
        self.user.save()
        self.user.refresh_from_db()
        self.other_user: User = generate_user(username='other_user')
        self.token = self.generate_access_token(self.user)
        self.headers = {
            **self.generate_headers(),
            **self.bare_headers,
        }

        self.url = reverse('online_groups-list')
        self.id_url = lambda _id: self.url + str(_id) + '/'
        self.group_name = 'Noenkom'
        self.group_name_long = 'Noenkomiteen'
        self.group = G(Group, name=self.group_name)
        self.group_data = {
            'group': self.group.id,
            'name_short': self.group_name,
            'name_long': self.group_name_long,
        }
        self.create_group = lambda: OnlineGroup.objects.create(
            group=self.group,
            name_short=self.group_name,
            name_long=self.group_name_long
        )

    def test_groups_returns_200(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_200(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_superuser_can_create_groups(self):
        response = self.client.post(self.url, self.group_data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_create_group_if_django_group_has_existing_online_group(self):
        self.create_group()

        response = self.client.post(self.url, self.group_data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('group'), ['Denne Djangogruppen har allerede en Onlinegruppe'])

    def test_cannot_create_online_group_without_django_group(self):
        wrong_group_id = -1
        response = self.client.post(self.url, {
            **self.group_data,
            'group': wrong_group_id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('group'), [f'Ugyldig pk "{wrong_group_id}" - objektet eksisterer ikke.'])

    def test_regular_user_cannot_create_groups(self):
        self.user.is_superuser = False
        self.user.save()

        response = self.client.post(self.url, self.group_data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get('message'), 'Du har ikke tillatelse til å opprette grupper')

    def test_users_with_permission_can_create_groups(self):
        self.user.is_superuser = False
        self.user.save()
        permission = Permission.objects.get(codename='add_onlinegroup')
        self.user.user_permissions.add(permission)

        response = self.client.post(self.url, self.group_data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_superuser_can_delete_group(self):
        online_group = self.create_group()

        response = self.client.delete(self.id_url(online_group.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_regular_user_cannot_delete_group(self):
        online_group = self.create_group()
        self.user.is_superuser = False
        self.user.save()

        response = self.client.delete(self.id_url(online_group.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_group_leader_can_delete_group(self):
        online_group = self.create_group()
        membership = GroupMember.objects.create(group=online_group, user=self.user)
        GroupRole.objects.create(membership=membership, role_type=RoleType.LEADER)
        self.user.is_superuser = False
        self.user.save()

        response = self.client.delete(self.id_url(online_group.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_deputy_group_leader_can_delete_group(self):
        online_group = self.create_group()
        membership = GroupMember.objects.create(group=online_group, user=self.user)
        GroupRole.objects.create(membership=membership, role_type=RoleType.DEPUTY_LEADER)
        self.user.is_superuser = False
        self.user.save()

        response = self.client.delete(self.id_url(online_group.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class GroupMemberTestCase(OIDCTestCase):

    def setUp(self):
        self.user: User = generate_user(username='test_user')
        self.user.is_superuser = True
        self.user.save()
        self.user.refresh_from_db()
        self.other_user: User = generate_user(username='other_user')
        self.token = self.generate_access_token(self.user)
        self.headers = {
            **self.generate_headers(),
            **self.bare_headers,
        }

        self.url = reverse('group_members-list')
        self.id_url = lambda _id: self.url + str(_id) + '/'
        self.group_name = 'Noenkom'
        self.group_name_long = 'Noenkomiteen'
        self.group = G(Group, name=self.group_name)
        self.group_data = {
            'group': self.group.id,
            'name_short': self.group_name,
            'name_long': self.group_name_long,
        }
        self.create_group = lambda: OnlineGroup.objects.create(
            group=self.group,
            name_short=self.group_name,
            name_long=self.group_name_long
        )
        self.online_group = self.create_group()

        self.membership_data = {
            'group': self.online_group.id,
            'user': self.user.id,
        }
        self.create_membership = lambda: GroupMember.objects.create(user=self.user, group=self.online_group)

    def test_group_members_returns_200(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_200(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_superuser_can_create_memberships(self):
        self.user.save()
        response = self.client.post(self.url, self.membership_data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_have_multiple_memberships_in_one_group(self):
        self.create_membership()
        response = self.client.post(self.url, self.membership_data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('non_field_errors'), ['Feltene user, group må gjøre et unikt sett.'])

    def test_regular_user_cannot_create_groups(self):
        self.user.is_superuser = False
        self.user.save()

        response = self.client.post(self.url, self.membership_data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get('message'), 'Du har ikke tillatelse til å opprette gruppemedlemskap')

    def test_users_with_permission_can_create_memberships(self):
        self.user.is_superuser = False
        self.user.save()
        permission = Permission.objects.get(codename='add_groupmember')
        self.user.user_permissions.add(permission)

        response = self.client.post(self.url, self.membership_data, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_superuser_can_delete_memberships(self):
        membership = self.create_membership()

        response = self.client.delete(self.id_url(membership.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_regular_user_cannot_delete_memberships(self):
        self.user.is_superuser = False
        self.user.save()
        membership = self.create_membership()

        response = self.client.delete(self.id_url(membership.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_group_leader_can_delete_memberships(self):
        membership = self.create_membership()
        GroupRole.objects.create(membership=membership, role_type=RoleType.LEADER)
        self.user.is_superuser = False
        self.user.save()

        response = self.client.delete(self.id_url(membership.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_deputy_group_leader_can_delete_memberships(self):
        membership = self.create_membership()
        GroupRole.objects.create(membership=membership, role_type=RoleType.DEPUTY_LEADER)
        self.user.is_superuser = False
        self.user.save()

        response = self.client.delete(self.id_url(membership.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class GroupRoleTestCase(OIDCTestCase):

    def setUp(self):
        self.user: User = generate_user(username='test_user')
        self.user.is_superuser = True
        self.user.save()
        self.user.refresh_from_db()
        self.other_user: User = generate_user(username='other_user')
        self.token = self.generate_access_token(self.user)
        self.headers = {
            **self.generate_headers(),
            **self.bare_headers,
        }

        self.url = reverse('group_roles-list')
        self.id_url = lambda _id: self.url + str(_id) + '/'
        self.group_name = 'Noenkom'
        self.group_name_long = 'Noenkomiteen'
        self.group = G(Group, name=self.group_name)
        self.group_data = {
            'group': self.group.id,
            'name_short': self.group_name,
            'name_long': self.group_name_long,
        }
        self.create_group = lambda: OnlineGroup.objects.create(
            group=self.group,
            name_short=self.group_name,
            name_long=self.group_name_long
        )
        self.online_group = self.create_group()

        self.membership_data = {
            'group': self.online_group.id,
            'user': self.user.id,
        }
        self.create_membership = lambda: GroupMember.objects.create(user=self.user, group=self.online_group)
        self.membership = self.create_membership()

        self.get_role_data = lambda role_type: {
            'membership': self.membership.id,
            'role_type': role_type,
        }
        self.create_role = lambda role_type: GroupRole.objects.create(
            membership=self.membership,
            role_type=role_type
        )

    def test_roles_returns_200(self):
        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_un_authenticated_user_gets_200(self):
        response = self.client.get(self.url, **self.bare_headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_superuser_can_create_roles(self):
        response = self.client.post(self.url, self.get_role_data(RoleType.MEMBER), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_member_cannot_have_the_same_role_twice_in_a_single_group(self):
        self.create_role(RoleType.MEMBER)
        response = self.client.post(self.url, self.get_role_data(RoleType.MEMBER), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get('non_field_errors'),
            ['Feltene membership, role_type må gjøre et unikt sett.']
        )

    def test_group_member_can_have_different_role_types_in_the_same_group(self):
        self.create_role(RoleType.LEADER)
        response = self.client.post(self.url, self.get_role_data(RoleType.MEMBER), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_singluar_role_types_can_only_appear_once_for_each_group(self):
        other_user: User = G(User, username='test_wrong_person')
        membership = GroupMember.objects.create(user=other_user, group=self.online_group)

        self.create_role(RoleType.LEADER)
        response = self.client.post(self.url, {
            **self.get_role_data(RoleType.LEADER),
            'membership': membership.id,
        }, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json().get('non_field_errors'),
            [f'Det finnes allerede et gruppemedlem med rollen "{RoleType.LEADER}"']
        )

    def test_regular_user_cannot_create_roles(self):
        self.user.is_superuser = False
        self.user.save()

        response = self.client.post(self.url, self.get_role_data(RoleType.MEMBER), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get('message'), 'Du har ikke tillatelse til å opprette gruppemedlemsroller')

    def test_users_with_permission_can_create_roles(self):
        self.user.is_superuser = False
        self.user.save()
        permission = Permission.objects.get(codename='add_grouprole')
        self.user.user_permissions.add(permission)

        response = self.client.post(self.url, self.get_role_data(RoleType.MEMBER), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_superuser_can_delete_roles(self):
        role = self.create_role(RoleType.MEMBER)

        response = self.client.delete(self.id_url(role.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_regular_user_cannot_delete_roles(self):
        self.user.is_superuser = False
        self.user.save()
        role = self.create_role(RoleType.MEMBER)

        response = self.client.delete(self.id_url(role.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_group_leader_can_delete_roles(self):
        self.user.is_superuser = False
        self.user.save()
        self.create_role(RoleType.LEADER)
        role = self.create_role(RoleType.MEMBER)

        response = self.client.delete(self.id_url(role.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_deputy_group_leader_can_delete_roles(self):
        self.user.is_superuser = False
        self.user.save()
        self.create_role(RoleType.DEPUTY_LEADER)
        role = self.create_role(RoleType.MEMBER)

        response = self.client.delete(self.id_url(role.id), **self.headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
