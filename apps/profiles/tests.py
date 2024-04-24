from django.test import TestCase
from django.urls import reverse
from django_dynamic_fixture import G

from apps.authentication.models import OnlineUser as User
from apps.profiles.forms import ZIP_CODE_VALIDATION_ERROR, ProfileForm
from apps.profiles.models import Privacy


class ProfileInitTestCase(TestCase):
    def test_privacy_profile_save(self):
        user = G(User)
        self.assertTrue(Privacy.objects.filter(user=user).exists())


class ProfileViewEditTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._url = reverse("profile_edit")
        cls._user = G(User)

    def setUp(self):
        self.client.force_login(self._user)

    def test_profile_retrieve(self):
        response = self.client.get(self._url)

        self.assertEqual(200, response.status_code)

    def test_profile_save(self):
        response = self.client.post(self._url)

        self.assertEqual(200, response.status_code)

    def test_profile_save_valid_zip(self):
        data = {"zip_code": 7030}

        response = self.client.post(self._url, data)

        self.assertEqual(200, response.status_code)

    def test_profile_save_invalid_zip(self):
        data = {"zip_code": 123}

        response = self.client.post(self._url, data)

        self.assertFormError(
            form=response.context["user_profile_form"],
            field="zip_code",
            errors=[ZIP_CODE_VALIDATION_ERROR],
        )


class ProfileEditFormTestCase(TestCase):
    def test_profile_form_valid_zip(self):
        data = {"gender": "male", "zip_code": 7030}
        form = ProfileForm(data=data)

        self.assertTrue(form.is_valid())

    def test_profile_form_invalid_zip(self):
        data = {"gender": "male", "zip_code": 123}
        form = ProfileForm(data=data)

        self.assertFalse(form.is_valid())
