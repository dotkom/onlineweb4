from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import MembershipApproval, Approval
from .tasks import send_approval_notification, send_approval_status_update


@receiver(post_save, sender=MembershipApproval)
def new_membership_approval_handler(sender, instance, created, **kwargs):
    """

    :param sender: The sending model.
    :type sender: MembershipApproval
    :param instance: The MembershipApproval instance
    :type instance: MembershipApproval
    :param created: True or False, whether this instance is new or not.
    :type created: bool
    :param kwargs: Other parameters.
    :type kwargs: dict
    :return: Nothing
    :rtype: None
    """

    if created:
        if settings.APPROVAL_SETTINGS.get('SEND_APPROVER_NOTIFICATION_EMAIL', False):
            send_approval_notification(instance)


@receiver(post_save, sender=Approval)
def notify_membership_applicant_handler(sender, instance, approved, **kwargs):
    """

       :param sender: The sending model.
       :type sender: MembershipApproval
       :param instance: The Approval instance
       :type instance: Approval
       :param approved: True or False, whether this instance is approved or not.
       :type approved: bool
       :param kwargs: Other parameters.
       :type kwargs: dict
       :return: Nothing
       :rtype: None
    """

    if approved:
        if len(instance.applicant.get_email()) > 0:
            send_approval_status_update(instance)
