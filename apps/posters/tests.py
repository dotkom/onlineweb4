from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.test import TestCase, override_settings
from django.urls import reverse
from django_dynamic_fixture import G

from apps.authentication.models import Email
from apps.authentication.models import OnlineUser as User
from apps.posters.models import Poster


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

        group = G(Group, name="Komiteer")

        ow4_gsuite_sync = settings.OW4_GSUITE_SYNC
        ow4_gsuite_sync["ENABLED"] = False
        with override_settings(OW4_GSUITE_SYNC=ow4_gsuite_sync):
            user.groups.add(group)
            user.save()

        # Create prokom group as permissions are assigned to prokom after creation
        G(Group, name="proKom")
        # Create dotkom group because the redirect assertion wants to check if the user is in dotkom group
        G(Group, name="dotKom")

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
