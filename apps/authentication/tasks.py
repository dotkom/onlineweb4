import logging

from celery.schedules import crontab
from django.conf import settings
from django.contrib.auth.models import Group

from apps.authentication.models import OnlineGroup
from apps.authentication.models import OnlineUser as User
from onlineweb4.celery import app


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **_kwargs):
    sender.add_periodic_task(
        crontab(hour=7, minute=30),
        synchronize_groups.s(),
    )


@app.task
def synchronize_groups():
    logger = logging.getLogger(f"syncer.{__name__}")

    if hasattr(settings, "GROUP_SYNCER"):
        logger.info("Running group syncer.")
        sync(logger)


def sync(logger):
    # Loop all the syncs
    for job in settings.GROUP_SYNCER:
        # Log what job we are running
        logger.info("Started: " + job.get("name"))

        add_users(job, logger)
        remove_users(job, logger)


def add_users(group, logger):

    # FORWARD SYNC
    # Syncing users from source groups to destination groups

    # Get all users in the source groups
    users_in_source = User.objects.filter(groups__id__in=group.get("source")).exclude(
        groups__id__in=group.get("destination")
    )

    # Check if any users were found
    if len(users_in_source) > 0:
        # Loop all destination groups
        for destination_group in group.get("destination"):
            # Create object for the current destination group
            destination_group_object = Group.objects.get(id=destination_group)

            # Loop all the users in the source groups
            for user in users_in_source:
                # Get all groups for the current user
                user_groups = user.groups.all()

                # Check if the user has the current destination group
                if destination_group_object not in user_groups:
                    # User is not in the current destination group, add
                    destination_group_object.user_set.add(user)
                    logger.info(
                        f"{user} added to group {destination_group_object.name}"
                    )


def remove_users(group, logger):

    # BACKWARDS SYNC
    # Removing users from destination group(s) if they are not in the source group(s)

    # Get all users in the destination groups
    users_in_destination = (
        User.objects.filter(groups__id__in=group.get("destination"))
        .all()
        .exclude(groups__id__in=group.get("source"))
    )

    # Check if any users were found
    if len(users_in_destination) > 0:
        # Loop all the users in the destination groups
        for user in users_in_destination:
            user_in_source_group = False
            user_groups = user.groups.all()

            # Get all groups the user is in
            for user_group in user_groups:
                # Check if the current user group is in the source list
                if user_group.id in group.get("source"):
                    # User group was found
                    user_in_source_group = True

                    # Break out of the loop
                    break

            # Check if user was found in any of the source groups
            if not user_in_source_group:
                # User was not found, remove from all destination groups
                for user_group in user_groups:
                    # Check if current group is in destination groups
                    if user_group.id in group.get("destination"):
                        # This group is a destination group, remove it from the user
                        destination_group = Group.objects.filter(
                            id=user_group.id
                        ).first()
                        destination_group.user_set.remove(user)
                        logger.info(
                            f"{user} removed from group {destination_group.name}"
                        )


@app.task(bind=True)
def assign_permission_from_group_admins(self, group_id: int):
    """
    Assign permission to handle groups recursively for all members of a group and sub groups.
    This task should be run when there are changes to which users should manage the group.
    """

    def assign_perms(group: OnlineGroup):
        group.assign_permissions()
        for member in group.members.all():
            member.assign_permissions()
        for sub_group in group.sub_groups.all():
            assign_perms(sub_group)

    origin_group = OnlineGroup.objects.get(pk=group_id)
    assign_perms(group=origin_group)
