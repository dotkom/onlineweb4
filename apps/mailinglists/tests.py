from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.reverse import reverse

from apps.mailinglists.models import MailEntity, MailGroup
from apps.online_oidc_provider.test import OIDCTestCase


class MailTestMixin(OIDCTestCase):
    def setUp(self):
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


class MailGroupTests(MailTestMixin):
    def setUp(self):
        self.url = reverse("mailinglists_groups-list")
        super().setUp()

    def test_add_mail_group_adds_mail_entity_signal(self):
        assign_perm("mailinglists.add_mailgroup", self.user)

        response = self.client.post(
            self.url,
            {
                "name": "Linjeforeninger på Gløshaugen",
                "email_local_part": "gloshaugen",
                "domain": MailGroup.Domains.ONLINE_NTNU_NO,
                "description": "En haug i Trondheim",
            },
            **self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mailinglist = response.data

        mail = MailEntity.objects.get(name=mailinglist.get("name"))

        self.assertEqual(mail.description, mailinglist.get("description"))
        self.assertEqual(mail.email, mailinglist.get("email"))
        self.assertEqual(mail.public, mailinglist.get("public"))

    def test_anon_get(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_authenticated_get(self):
        assign_perm("mailinglists.view_mailgroup", self.user)

        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)


class MailEntityTests(MailTestMixin):
    def setUp(self):
        self.url = reverse("mailinglists_entities-list")
        super().setUp()

    def test_anon_get(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_authenticated_get(self):
        assign_perm("mailinglists.view_mailentity", self.user)

        response = self.client.get(self.url, **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 4)

    def test_get_associated_entities(self):
        assign_perm("mailinglists.view_mailentity", self.user)

        response = self.client.get(f"{self.url}?groups={self.group.id}", **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
