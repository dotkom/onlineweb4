from collections import OrderedDict

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django_dynamic_fixture import G
from rest_framework import status
from rest_framework.reverse import reverse

from apps.authentication.models import OnlineUser
from apps.mailinglists.models import MailEntity, MailGroup
from apps.online_oidc_provider.test import OIDCTestCase


class MailTestMixin(OIDCTestCase):
    def setUp(self) -> None:
        self.beta = MailEntity.objects.create(
            email="hs@beta.ntnu.no",
            name="Beta Linjeforening",
            description="Vi er kanskje ikke Alfa, men vi er bedre enn Gamma.",
            public=True,
        )
        self.gamma = MailEntity.objects.create(
            email="hs@gamma.ntnu.no",
            name="Gamma Linjeforening",
            description="Lorem ipsum dolor sit amed.",
            public=False,
        )
        self.group = MailGroup.objects.create(
            email_local_part="gresk",
            name="Greske linjeforeninger",
            domain=MailGroup.Domains.LINJEFORENINGER_NO,
            description="Linjeforenigner med greske navn.",
        )
        self.group2 = MailGroup.objects.create(
            email_local_part="empty",
            name="The Empty List",
            domain=MailGroup.Domains.ONLINE_NTNU_NO,
            description="En mystisk liste",
            public=False,
        )
        self.group.members.add(self.beta, self.gamma)

        self.user = G(OnlineUser)
        self.token = self.generate_access_token(self.user)


class MailGroupTests(MailTestMixin):
    def setUp(self):
        self.url = reverse("mailinglists-list")
        super().setUp()

    def test_add_mail_group_adds_mail_entity_signal(self):
        content_type = ContentType.objects.get_for_model(MailGroup)
        permission = Permission.objects.get(
            codename="add_mailgroup", content_type=content_type
        )
        self.user.user_permissions.add(permission)

        response = self.client.post(
            self.url,
            {
                "name": "Linjeforeninger på Gløshaugen",
                "email_local_part": "gloshaugen",
                "domain": MailGroup.Domains.ONLINE_NTNU_NO,
                "description": "En haug i Trondheim",
            },
        )
        mailinglist = response.data

        mail = MailEntity.objects.get(name=mailinglist.name)

        self.assertEqual(mail.description, mailinglist.description)
        self.assertEqual(mail.email, mailinglist.email)
        self.assertEqual(mail.public, mailinglist.public)

    def test_anon_get(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_authenticated_get(self):
        content_type = ContentType.objects.get_for_model(MailGroup)
        permission = Permission.objects.get(
            codename="view_mailgroup", content_type=content_type
        )
        self.user.user_permissions.add(permission)

        response = self.client.get(self.url, {**self.generate_headers()})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)


class MailEntityTests(MailTestMixin):
    def setUp(self):
        self.url = reverse("mailinglists-list")
        super().setUp()

    def test_anon_get(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_authenticated_get(self):
        content_type = ContentType.objects.get_for_model(MailEntity)
        permission = Permission.objects.get(
            codename="view_mailentity", content_type=content_type
        )
        self.user.user_permissions.add(permission)

        response = self.client.get(self.url, {**self.generate_headers()})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)

    def test_get_associated_entities(self):
        content_type = ContentType.objects.get_for_model(MailEntity)
        permission = Permission.objects.get(
            codename="view_mailentity", content_type=content_type
        )
        self.user.user_permissions.add(permission)

        response = self.client.get(
            f"{self.url}?groups={self.group.id}", {**self.generate_headers()}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
