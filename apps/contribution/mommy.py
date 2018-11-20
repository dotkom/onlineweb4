import json

import requests
from django.utils import timezone
from pytz import timezone as tz

from apps.contribution.models import Repository, RepositoryLanguage
from apps.mommy import schedule
from apps.mommy.registry import Task

git_domain = "https://api.github.com"


class UpdateRepositories(Task):

    @staticmethod
    def run():
        # Load new data
        fresh = UpdateRepositories.get_git_repositories()
        localtz = tz('Europe/Oslo')
        for repo in fresh:
            fresh_repo = Repository(
                id=int(repo['id']),
                name=repo['name'],
                description=repo['description'],
                updated_at=localtz.localize(timezone.datetime.strptime(repo['updated_at'], "%Y-%m-%dT%H:%M:%SZ")),
                url=repo['url'],
                public_url=repo['html_url'],
                issues=repo['open_issues_count']
            )

            # If repository exists, only update data
            if Repository.objects.filter(id=fresh_repo.id).exists():
                stored_repo = Repository.objects.get(id=fresh_repo.id)
                repo_languages = UpdateRepositories.get_repository_languages(stored_repo.url)
                UpdateRepositories.update_repository(stored_repo, fresh_repo, repo_languages)

            # else: repository does not exist
            else:
                repo_languages = UpdateRepositories.get_repository_languages(fresh_repo.url)
                UpdateRepositories.new_repository(fresh_repo, repo_languages)

        # Delete repositories that does not satisfy the updated_at limit
        old_repositories = Repository.objects.all()
        for repo in old_repositories:
            if repo.updated_at < timezone.now() - timezone.timedelta(days=730):
                repo.delete()

    @staticmethod
    def update_repository(stored_repo, fresh_repo, repo_languages):
        stored_repo.name = fresh_repo.name
        stored_repo.description = fresh_repo.description
        stored_repo.updated_at = fresh_repo.updated_at
        stored_repo.url = fresh_repo.url
        stored_repo.public_url = fresh_repo.public_url
        stored_repo.issues = fresh_repo.issues
        stored_repo.save()

        # Update languages if they exist, and add if not
        for language in repo_languages:
            if RepositoryLanguage.objects.filter(type=language, repository=stored_repo).exists():
                stored_language = RepositoryLanguage.objects.get(type=language, repository=stored_repo)
                stored_language.size = repo_languages[language]
                stored_language.save()
            else:
                new_language = RepositoryLanguage(
                    type=language,
                    size=(int(repo_languages[language])),
                    repository=stored_repo
                )
                new_language.save()

    @staticmethod
    def new_repository(new_repo, new_languages):
        # Filter out repositories with inactivity past 2 years (365 days * 2)
        if new_repo.updated_at > timezone.now() - timezone.timedelta(days=730):
            new_repo = Repository(
                id=new_repo.id,
                name=new_repo.name,
                description=new_repo.description,
                updated_at=new_repo.updated_at,
                url=new_repo.url,
                public_url=new_repo.public_url,
                issues=new_repo.issues
            )
            new_repo.save()

            # Add repository languages
            for language in new_languages:
                new_language = RepositoryLanguage(
                    type=language,
                    size=int(new_languages[language]),
                    repository=new_repo
                )
                new_language.save()

    @staticmethod
    def get_git_repositories():
        url = git_domain + "/users/dotkom/repos?per_page=60"
        r = requests.get(url)
        data = json.loads(r.text)
        return data

    @staticmethod
    def get_repository_languages(url):
        r = requests.get(url + "/languages")
        data = json.loads(r.text)
        return data


schedule.register(UpdateRepositories, day_of_week="mon-sun", hour=6, minute=0)
