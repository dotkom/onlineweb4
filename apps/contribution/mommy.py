from apps.mommy import schedule
from apps.mommy.registry import Task
from apps.contribution.models import Repository

import json
import requests

git_domain = "https://api.github.com"


class UpdateRepositories(Task):

    @staticmethod
    def run():
        UpdateRepositories.refresh_repositories()

    @staticmethod
    def refresh_repositories():
        print("UPDATING REPOSITORIES")

        # Delete all to get fresh data
        Repository.objects.delete()

        # Load new data
        fresh = UpdateRepositories.get_git_repositories()
        for repo in fresh:
            new_repo = Repository(
                id=repo['id'],
                name=repo['name'],
                description=repo['description'],
                updated_at=repo['updated_at'],
                url=repo['url']
            )
            new_repo.save()

    @staticmethod
    def get_git_repositories():
        url = git_domain + "/users/dotkom/repos"
        r = requests.get(url)
        data = json.loads(r.text)
        return data


schedule.register(UpdateRepositories, day_of_week="mon-sun", hour=7, minute=0)
