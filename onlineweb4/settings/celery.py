from decouple import config

# Runs task sync instead of async. Good for development when the broker isn't running
CELERY_TASK_ALWAYS_EAGER = config(
    "OW4_CELERY_TASK_ALWAYS_EAGER", cast=bool, default=True
)
# Propagate exceptions from the task like normal exceptions
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = config("OW4_CELERY_BROKER_URL", default="redis://localhost:6379/0")
