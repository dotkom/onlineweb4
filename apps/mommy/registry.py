# encoding: utf-8

"""
A simple usage example, runs task every 5 seconds:

    class DummyTask(Task):
        @staticmethod
        def run():
            pass

    schedule.register(dummyTask, second="*/5")

For keyword arguments to schedule.register see:
http://pythonhosted.org/APScheduler/cronschedule.html
"""

class Task(object):
    """
    A Task object ment to be inherited. Contains default values
    """
    task_name = ""  # A human readable task_name.

    user_override_email = False  # user can configurate email from this task
    user_default_email = True  # The default configuration for the user

    user_override_notification = False  # user can configure
    user_default_notification = True  # default for user

    @staticmethod
    def run():
        raise NotImplementedError("you must define a run() method for your task")

    def __repr__(self):
        return "<Task: %s>" % self.task_name

    def __str__(self):
        return self.task_name

class Schedule(object):
    """A Schedule containing tasks"""

    def __init__(self):
        self._task_names = []
        self._tasks = {}

    def register(self, task, **kwargs):
        if(task in self._tasks):
            raise ValueError("Could not register %s, already registered", task.__name__)
        if(task.__name__ in self._tasks):
            raise ValueError("Could not register %s, a task with the same name already registered")


        self._tasks[task] = kwargs

    @property
    def tasks(self):
        return self._tasks
