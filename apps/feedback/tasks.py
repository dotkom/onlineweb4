import logging

from onlineweb4.celery import app

from .models import Session

logger = logging.getLogger(__name__)


def handle_clear_session(session: Session):
    """
    Remove all related data resulting from a stale session, as well as the session itself.
    """
    session.field_of_study_answers.all().delete()
    session.multiple_choice_answers.all().delete()
    session.text_answers.all().delete()
    session.rating_answers.all().delete()
    session.delete()


@app.task(bind=True)
def clear_session_task(_, session_id: int):
    """
    Asynchronously clear a session after a given time if it still exists
    """
    session = Session.objects.filter(pk=session_id).first()
    if session and app.conf.task_always_eager is False:
        handle_clear_session(session)
