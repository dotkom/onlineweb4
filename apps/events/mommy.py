from apps.mommy import Task, schedule

class dummyTask(Task):
    def run():
        print "heidu"

schedule.register(dummyTask)
