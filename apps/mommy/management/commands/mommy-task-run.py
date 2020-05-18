from django.core.management.base import BaseCommand

from apps import mommy


class Command(BaseCommand):
    help = "run a job"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        mommy.autodiscover()

    def add_arguments(self, parser):
        parser.add_argument("job", help="name of job", choices=Command.job_names())

    @staticmethod
    def job_names():
        possible_jobs = []
        for task, _ in mommy.schedule.tasks.items():
            possible_jobs.append(task.__name__)
        return possible_jobs

    def handle(self, *args, **options):
        mommy.autodiscover()

        # run shit
        do_name = options["job"]
        for task, _ in mommy.schedule.tasks.items():
            if task.__name__ == do_name:
                task.run()
                return
        print("could not find job:" + do_name)
