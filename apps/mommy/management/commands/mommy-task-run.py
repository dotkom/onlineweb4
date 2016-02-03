from django.core.management.base import BaseCommand
from apps import mommy


class Command(BaseCommand):
    args = 'name of job'
    help = 'run a job'

    @staticmethod
    def print_job_names():
        possible_jobs = []
        for task, _ in mommy.schedule.tasks.items():
            possible_jobs.append(task.__name__)
        print("possible jobs:" + str(possible_jobs))

    def handle(self, *args, **options):
        mommy.autodiscover()

        if len(args) == 0:
            self.print_job_names()
            return

        # run shit
        do_name = args[0]
        for task, _ in mommy.schedule.tasks.items():
            if task.__name__ == do_name:
                task.run()
                return
        print("could not find job:" + do_name)
