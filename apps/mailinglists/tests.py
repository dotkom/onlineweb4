from django.test import TestCase

from apps.mailinglists.models import MailGroup, MailEntity


class MailGroupTests(TestCase):
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
