from apps.mommy import Task, schedule
import sys

class dummyTask(Task):

    @staticmethod
    def run():
        print  >> sys.stderr, 'spam'
        print "heidu"
        1/0

schedule.register(dummyTask, second="*/5")
