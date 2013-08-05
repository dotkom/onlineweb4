Mommy-scheduler
===============

This is a very simple wrapper for [APSchduler](http://pythonhosted.org/APScheduler/) for Django.

## configuration:
None. More from APwrapper could be added, surely.

## Setup:
Add `mommy` to installed apps and add this to the global `urls.py`: 

```python
import mommy

mommy.autodiscover()
mommy.run()
```

the code above will automatically discover all apps with mommy.py and add them
to the schedule, then run the scheduler.

An example of a mommy.py file, defining a task that gets run every 5 seconds:

```python
from apps.mommy import Task, schedule

class DummyTask(Task):

    @staticmethod
    def run():
        pass

schedule.register(DummyTask, second="*/5")
```
keyword arguments for schedule.register can be found
[here](http://pythonhosted.org/APScheduler/cronschedule.html)

### Optional:

Add logging of scheduled jobs to django, you need to add a logger for "apscheduler.schedule". An example of LOGGING in settings.py

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'apscheduler.scheduler': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
}
```

## Limitations:
For the scheduler to start running, one must load urls.py. 
This is done my doing a simple pageload somewhere in your application, and you
only need to do it *once*
