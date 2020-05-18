from django.test import TestCase
from django.utils import timezone
from django_dynamic_fixture import G

from apps.contribution.models import Repository, RepositoryLanguage
from apps.contribution.mommy import UpdateRepositories


# contribution.mommy tests
class UpdateRepositoriesTest(TestCase):
    def setUp(self):
        self.now = timezone.now()
        self.repo = G(
            Repository,
            id=1234,
            name="Test1",
            description="This is a repo for testing",
            updated_at=self.now,
            url="https://www.google.com",
            public_url="https://google.com",
            issues=2,
        )

        self.language_js = G(
            RepositoryLanguage, type="JavaScript", size=64000, repository=self.repo
        )

    def testRepositoryUpdate(self):
        local_now = timezone.now()
        fresh_repo = G(
            Repository,
            id=1234,
            name="Test2",
            description="This is a repo for testing2",
            updated_at=local_now,
            url="https://www.google.com/kittens",
            public_url="https://google.com/humpbackwhale",
            issues=4,
        )

        fresh_languages = {"JavaScript": 80000}

        UpdateRepositories.update_repository(self.repo, fresh_repo, fresh_languages)
        self.assertEqual(fresh_repo.name, self.repo.name)
        self.assertEqual(fresh_repo.description, self.repo.description)
        self.assertEqual(fresh_repo.updated_at, self.repo.updated_at)
        self.assertEqual(fresh_repo.url, self.repo.url)
        self.assertEqual(fresh_repo.public_url, self.repo.public_url)
        self.assertEqual(fresh_repo.issues, self.repo.issues)
        self.assertEqual(fresh_repo.languages, self.repo.languages)

    def testRepositoryCreation(self):
        local_now = timezone.now()
        fresh_repo = G(
            Repository,
            id=4567,
            name="Test3",
            description="This is a repo for testing3",
            updated_at=local_now,
            url="https://www.google.com/kittens/3",
            public_url="https://google.com/kiwi",
            issues=1,
        )

        fresh_languages = {"PythonScript": 90000}

        UpdateRepositories.new_repository(fresh_repo, fresh_languages)
        stored_repo = Repository.objects.get(id=4567)
        self.assertEqual(stored_repo.name, fresh_repo.name)
        self.assertEqual(stored_repo.description, fresh_repo.description)
        self.assertEqual(stored_repo.updated_at, fresh_repo.updated_at)
        self.assertEqual(stored_repo.url, fresh_repo.url)
        self.assertEqual(stored_repo.public_url, fresh_repo.public_url)
        self.assertEqual(stored_repo.issues, fresh_repo.issues)

        stored_language = stored_repo.languages.get(type="PythonScript")
        self.assertEqual(stored_language.size, fresh_languages["PythonScript"])
