# encoding: utf-8
import logging

from .registry import Schedule

logger = logging.getLogger(__name__)
default_app_config = 'apps.mommy.appconfig.MommyConfig'
schedule = Schedule()


def autodiscover():
    """
    imports mommy.py modules from all INSTALLED_APPS.
    """

    from importlib import import_module
    from django.conf import settings
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        # Attempt to import the app's mommy module.
        try:
            import_module('%s.mommy' % app)
        except ImportError:
            # silently fail if mommy module does not exist
            if module_has_submodule(mod, 'mommy'):
                raise


def run(**kwargs):
    """
    imports appscheduler, registers scheduled jobs, runs the scheduler
    """
    from apscheduler.schedulers.blocking import BlockingScheduler

    sched = BlockingScheduler(**kwargs)

    for task, kwargs in schedule.tasks.items():
        sched.add_job(task.run, trigger='cron', name=task.__name__, **kwargs)

    sched.start()  # main loop
