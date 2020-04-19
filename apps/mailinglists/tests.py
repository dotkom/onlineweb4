from collections import OrderedDict

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django_dynamic_fixture import G
from rest_framework import status
from rest_framework.reverse import reverse

from apps.authentication.models import OnlineUser
from apps.mailinglists.models import MailEntity, MailGroup
from apps.online_oidc_provider.test import OIDCTestCase


class MailGroupTests(OIDCTestCase):
    def setUp(self):
        self.url = reverse("mailinglists-list")
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

    def test_create_mail_group_adds_mail_entity_signal(self):
        mailinglist = MailGroup.objects.create(
            name="Linjeforeninger på Gløshaugen",
            email_local_part="gloshaugen",
            domain=MailGroup.Domains.ONLINE_NTNU_NO,
            description="En haug i Trondheim",
        )

        mail = MailEntity.objects.get(name=mailinglist.name)

        self.assertEqual(mail.description, mailinglist.description)
        self.assertEqual(mail.email, mailinglist.email)
        self.assertEqual(mail.public, mailinglist.public)

    def test_anon_api_call(self):
        # FIXME: Make this test pass by filtering out maillist's non-public emails
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["results"],
            [
                OrderedDict(
                    [
                        ("id", 1),
                        ("email", "gresk@linjeforeninger.no"),
                        ("name", "Greske linjeforeninger"),
                        ("description", "Linjeforenigner med greske navn."),
                        ("public", True),
                        (
                            "members",
                            [
                                OrderedDict(
                                    [
                                        ("id", 1),
                                        ("email", "hs@beta.ntnu.no"),
                                        ("name", "Beta Linjeforening"),
                                        (
                                            "description",
                                            "Vi er kanskje ikke Alfa, men vi er bedre enn Gamma.",
                                        ),
                                        ("public", True),
                                    ]
                                )
                            ],
                        ),
                    ]
                )
            ],
        )

    def test_authenticated_api_call(self):
        # FIXME: Make this test pass
        content_type = ContentType.objects.get_for_model(MailGroup)
        permission = Permission.objects.get(
            codename="view_mailgroup", content_type=content_type
        )
        self.user.user_permissions.add(permission)

        self.assertTrue(self.user.has_perm("mailinglists.view_mailgroup"))

        response = self.client.get(self.url, {**self.generate_headers()})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["results"],
            [
                OrderedDict(
                    [
                        ("id", 1),
                        ("email", "gresk@linjeforeninger.no"),
                        ("name", "Greske linjeforeninger"),
                        ("description", "Linjeforenigner med greske navn."),
                        ("public", True),
                        (
                            "members",
                            [
                                OrderedDict(
                                    [
                                        ("id", 1),
                                        ("email", "hs@beta.ntnu.no"),
                                        ("name", "Beta Linjeforening"),
                                        (
                                            "description",
                                            "Vi er kanskje ikke Alfa, men vi er bedre enn Gamma.",
                                        ),
                                        ("public", True),
                                    ]
                                ),
                                OrderedDict(
                                    [
                                        ("id", 2),
                                        ("email", "hs@gamma.ntnu.no"),
                                        ("name", "Gamma Linjeforening"),
                                        ("description", "Lorem ipsum dolor sit amed."),
                                        ("public", False),
                                    ]
                                ),
                            ],
                        ),
                    ]
                ),
                OrderedDict(
                    [
                        ("id", 2),
                        ("email", "empty@online.ntnu.no"),
                        ("name", "The Empty List"),
                        ("description", "En mystisk liste"),
                        ("public", False),
                        ("members", []),
                    ]
                ),
            ],
        )
