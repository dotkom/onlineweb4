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
        # Load new data
        fresh = UpdateRepositories.get_git_repositories()
        for repo in fresh:
            repo_id = int(repo['id'])
            repo_updated = timezone.datetime.strptime(repo['updated_at'], "%Y-%m-%dT%H:%M:%SZ")
            repo_description = repo['description']
            repo_name = repo['name']
            repo_url = repo['url']
            repo_languages = UpdateRepositories.get_repository_languages(repo_url)

            # If repository exists, only update data
            if Repository.objects.filter(id=repo_id).exists():
                stored_repo = Repository.objects.get(id=repo_id)
                stored_repo.name = repo_name
                stored_repo.description = repo_description
                stored_repo.updated_at = repo_updated
                stored_repo.url = repo_url
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

            # else: repository does not exist
            else:
                # Filter out repositories with inactivity
                if repo_updated.year > timezone.now().year - 2:
                    new_repo = Repository(
                        id=repo_id,
                        name=repo_name,
                        description=repo_description,
                        updated_at=repo_updated,
                        url=repo_url
                    )
                    new_repo.save()

                    # Add repository languages
                    languages = UpdateRepositories.get_repository_languages(new_repo.url)
                    for language in languages:
                        new_language = RepositoryLanguage(
                            type=language,
                            size=int(languages[language]),
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


schedule.register(UpdateRepositories, day_of_week="mon-sun", hour=12, minute=10)
