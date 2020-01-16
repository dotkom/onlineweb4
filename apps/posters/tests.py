from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings
from django.urls import reverse
from django_dynamic_fixture import G

from apps.authentication.models import Email
from apps.authentication.models import OnlineUser as User
from apps.events.tests.utils import add_to_group, create_committee_group
from apps.posters.models import Poster

from .dashboard.utils import get_poster_admins


class PosterPermissionTestCase(TestCase):
    def setUp(self):
        self.ordering_group = create_committee_group(G(Group, name="Fagkom"))
        self.admin_group = create_committee_group(G(Group, name="Prokom"))
        self.super_user: User = G(User)
        self.super_user.is_superuser = True
        self.super_user.save()

        self.admin_user = G(User)
        add_to_group(self.admin_group, self.admin_user)
        content_type = ContentType.objects.get_for_model(Poster)
        self.all_permissions = Permission.objects.filter(content_type=content_type)
        for perm in self.all_permissions:
            self.admin_group.permissions.add(perm)

        self.ordering_user = G(User)
        add_to_group(self.ordering_group, self.ordering_user)

    def test_poster_admins(self):

        all_admin_users = get_poster_admins()

        self.assertIn(self.admin_user, all_admin_users)
        self.assertNotIn(self.super_user, all_admin_users)
        self.assertNotIn(self.ordering_user, all_admin_users)


class AddPosterTestCase(TestCase):
    def test_create_poster_order(self):
        url = reverse("posters_add", kwargs={"order_type": 3})

        user = G(User, username="test_user")
        G(Email, user=user, primary=True, verified=True)

        user.is_staff = True
        user.is_active = True
        perms = Permission.objects.filter(codename="add_poster_order")
        user.user_permissions.add(perms[0])

        user.save()

        self.client.force_login(user)

        group = G(Group)

        ow4_gsuite_sync = settings.OW4_GSUITE_SYNC
        ow4_gsuite_sync["ENABLED"] = False
        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            user.groups.add(group)
            user.save()

        data = {
            "title": "test",
            "description": "test",
            "comments": "test",
            "price": 1,
            "amount": 1,
            "ordered_committee": group.pk,
        }

        response = self.client.post(url, data)

        poster = Poster.objects.get(title=data["title"])

        self.assertEqual(data["title"], poster.title)
        self.assertRedirects(response, reverse("posters_detail", args=(poster.id,)))
