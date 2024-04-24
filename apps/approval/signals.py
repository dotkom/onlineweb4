from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.approval.models import Approval, MembershipApproval
from utils.disable_for_loaddata import disable_for_loaddata

from .tasks import send_approval_notification, send_approval_status_update


@receiver(post_save, sender=MembershipApproval)
@disable_for_loaddata
def new_membership_approval_handler(
    sender, instance: MembershipApproval, created=False, **kwargs
):
    """
    :param instance: The MembershipApproval instance
    :param created: True or False, whether this instance is new or not.
    """

    if (
        created
        and not instance.processed
        and settings.APPROVAL_SETTINGS.get("SEND_APPROVER_NOTIFICATION_EMAIL", False)
    ):
        send_approval_notification(instance)


@receiver(post_save, sender=MembershipApproval)
@disable_for_loaddata
def notify_membership_applicant_handler(
    sender, instance: Approval, created=False, **kwargs
):
    """
    :param sender: The sending model.
    :param instance: The Approval instance
    :param created: True or False, whether this instance is new or not.
    """

    if (
        not created
        and instance.processed
        and instance.applicant.email
        and settings.APPROVAL_SETTINGS.get("SEND_APPLICANT_NOTIFICATION_EMAIL", False)
    ):
        send_approval_status_update(instance)
