# encoding: utf-8
from .registry import Schedule

import logging

logger = logging.getLogger(__name__)
default_app_config = 'apps.mommy.appconfig.MommyConfig'
schedule = Schedule()


def autodiscover():
    """
    imports mommy.py modules from all INSTALLED_APPS.
    """

    from django.utils.importlib import import_module
    from django.conf import settings
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        # Attempt to import the app's mommy module.
        try:
            import_module('%s.mommy' % app)
        except:
            # silently fail if mommy module does not exist
            if module_has_submodule(mod, 'mommy'):
                raise


def run(**kwargs):
    """
    imports apscheduler, registers scheduled jobs, runs the scheduler
    """
    from apscheduler.scheduler import Scheduler

    sched = Scheduler(**kwargs)

    for task, kwargs in schedule.tasks.items():
        sched.add_cron_job(task.run, name=task.__name__, **kwargs)

    sched.start()  # main loop
