from django.test import TestCase

from apps.mailinglists.models import Mail, Mailinglist


class MailinglistTests(TestCase):
    def test_create_mailinglist_adds_mail_signal(self):
        mailinglist = Mailinglist.objects.create(
            name="Linjeforeninger på Gløshaugen",
            email_name="gloshaugen",
            description="En haug i Trondheim",
        )

        mail = Mail.objects.get(name=mailinglist.name)

        self.assertEqual(mail.description, mailinglist.description)
        self.assertEqual(mail.email, mailinglist.email)
        self.assertEqual(mail.public, mailinglist.public)
