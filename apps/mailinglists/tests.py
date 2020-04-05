from django.test import TestCase

from apps.mailinglists.models import Organization, MailGroup


class MailinglistTests(TestCase):
    def test_create_mailinglist_adds_mail_signal(self):
        mailinglist = MailGroup.objects.create(
            name="Linjeforeninger på Gløshaugen",
            email_name="gloshaugen",
            description="En haug i Trondheim",
        )

        mail = Organization.objects.get(name=mailinglist.name)

        self.assertEqual(mail.description, mailinglist.description)
        self.assertEqual(mail.email, mailinglist.email)
        self.assertEqual(mail.public, mailinglist.public)
