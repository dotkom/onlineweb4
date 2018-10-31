import json

import requests
from django.utils import timezone

from apps.contribution.models import Repository, RepositoryLanguage
from apps.mommy import schedule
from apps.mommy.registry import Task

git_domain = "https://api.github.com"


class UpdateRepositories(Task):

    @staticmethod
    def run():
        UpdateRepositories.refresh_repositories()

    @staticmethod
    def refresh_repositories():
        # Delete all to get fresh data
        Repository.objects.all().delete()

        # Load new data
        fresh = UpdateRepositories.get_git_repositories()
        for repo in fresh:

            # Filter out repositories with inactivity
            time = timezone.datetime.strptime(repo['updated_at'], "%Y-%m-%dT%H:%M:%SZ")
            if time.year > timezone.now().year - 2:
                new_repo = Repository(
                    id=int(repo['id']),
                    name=repo['name'],
                    description=repo['description'],
                    updated_at=time,
                    url=repo['url']
                )
                new_repo.save()

                # Add repository languages
                languages = UpdateRepositories.get_repository_languages(new_repo.url)
                for key in languages:
                    new_language = RepositoryLanguage(
                        type=key,
                        size=int(languages[key]),
                        repository=new_repo
                    )
                    new_language.save()

    @staticmethod
    def get_git_repositories():
        url = git_domain + "/users/dotkom/repos"
        r = requests.get(url)
        data = json.loads(r.text)
        return data

    @staticmethod
    def get_repository_languages(url):
        r = requests.get(url + "/languages")
        data = json.loads(r.text)
        return data


schedule.register(UpdateRepositories, day_of_week="mon-sun", hour=7, minute=0)
