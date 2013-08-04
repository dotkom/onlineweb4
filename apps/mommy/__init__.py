# encoding: utf-8
from registry import Task
from registry import Schedule
from utils import send_mail
from utils import send_notification
schedule = Schedule()

def autodiscover():
    """
    imports mommy.py modules from all INSTALLED_APPS.
    """
    import copy
    from importlib import import_module
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

def run():
    """
    imports apscheduler, registers scheduled jobs, runs the scheduler
    """
    from apscheduler.scheduler import Scheduler

    # Start the scheduler
    sched = Scheduler()
    sched.start()

    def logged_run(run, task):
        def log_and_run(*args, **kwargs):
            #TODO: figure out proper logging
            print "Running task: %s" % task.__name__
            return run(*args, **kwargs)
        return log_and_run

    print schedule.tasks
    for task, kwargs in schedule.tasks.iteritems():
       sched.add_cron_job(logged_run(task.run, task), **kwargs)
