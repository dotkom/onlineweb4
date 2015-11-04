# -*- encoding: utf-8 -*-


class Task(object):

    @staticmethod
    def run():
        raise NotImplementedError("you must define a run() method for your task")

    def __repr__(self):
        return "<Task: %s>" % self.task_name

    def __str__(self):
        return self.task_name


class Schedule(object):
    """
    A Schedule containing tasks
    """

    def __init__(self):
        self._task_names = []
        self._tasks = {}

    def register(self, task, **kwargs):
        if task in self._tasks:
            raise ValueError("Could not register %s, already registered", task.__name__)
        if task.__name__ in self._tasks:
            raise ValueError("Could not register %s, a task with the same name already registered")

        self._tasks[task] = kwargs

    @property
    def tasks(self):
        return self._tasks
