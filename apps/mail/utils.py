# encoding: utf-8
from django.contrib.auth.models import User
from django.core.mail import send_mail as djsend_mail
from models import MommyUserConfig
from models import Notification


def send_mail(caller, template, template_context, subject, to, fra):
    """
    Sends mail to users by rendering the template with the given context.

    :caller: The caller
    :template: path to the template
    :template_context: context sendt to the template
    :subject: the subject of the email
    :to: a User object or a list of Users
    :fra: email address
    :returns: None
    """
    if isinstance(to, User):
        to = []

    to = _filter_users_email(caller, to)
    if len(to) == 0:
        return  # no users wants this email

    to_emails = [u.email for u in to if u.email]
    body = get_template(template).render(Context(template_context))
    djsend_mail(subject, body, fra, to_emails)

def _filter_users_email(caller, users):
    """
    filters users depedant on caller.

    Creates a MommyUserConfig instance for User if it does not exist.
    """
    filtered_users = []
    for user in users:
        try:
            conf = MommyUserConfig.objects.get(user=user, task=caller.__name__)
        except ObjectDoesNotExist:
            conf = MommyUserConfig.objects.create(user=user,
                    task=caller.__name__,
                    email=caller.user_default_email,
                    notification=caller.user_default_notification)
        if conf.email:
            filtered_users.append(user)
    return filtere_users


def send_notification(caller, to, message):
    """
    Sends a notification to the users with the given message

    :caller: The caller
    :to: a User object of a list of Users
    :message: Stringrepresentation of the message
    :returns: None
    """
    if isinstance(to, User):
        to = []

    to = _filter_users_notification(caller, to)

    for user in to:
        Notification.objects.create(user=user, message=message)

def _filter_users_notification(caller, users):
    """
    filters users depedant on caller.

    Creates a MommyUserConfig instance for User if it does not exist.
    """
    filtered_users = []
    for user in users:
        try:
            conf = MommyUserConfig.objects.get(user=user, task=caller.__name__)
        except ObjectDoesNotExist:
            conf = MommyUserConfig.objects.create(user=user,
                    task=caller.__name__,
                    email=caller.user_default_email,
                    notification=caller.user_default_notification)
        if conf.notification:
            filtered_users.append(user)
    return filtere_users
