# -*- coding: utf-8 -*-
import datetime
import socket
import locale
import logging

from django.conf import settings
from django.contrib.auth.models import Group

from apps.authentication.models import OnlineUser as User
from apps.mommy import Task, schedule

class SynchronizeBedFagUsers(Task):

    @staticmethod
    def run():
        logger = logging.getLogger('bedfagsyncer')
        locale.setlocale(locale.LC_ALL, "en_US.utf8")
        
        SynchronizeBedFagUsers.sync_users(logger)
    
    @staticmethod
    def sync_users(logger):
        # Logging
        logger.info("Started syncing bedKom and fagKom users to common group.")
        
        # Number of synces done
        synces = 0
        
        # Define container for all users
        user_container = []
        
        # Get bedKom-group
        bedkom_group = Group.objects.get(id = settings.BEDKOM_GROUP_ID)
        
        # Append bedKom to list
        for user in bedkom_group.user_set.all():
            user_container.append(user)
        
        # Get fagKom group
        fagkom_group = Group.objects.get(id = settings.FAGKOM_GROUP_ID)
        
        # Append fagKom to list if user is not already there
        for user in fagkom_group.user_set.all():
            found = False
            for existing_user in user_container:
                if (user.id == existing_user.id):
                    found = True
                    break
                
            if (found == False):
                user_container.append(user)
        
        # Load object for the common group
        COMMON_GROUP_OBJ = Group.objects.get(id = settings.COMMON_GROUP_ID)
        
        # Loop the list of all users we have by now
        for user in user_container:
            is_already_member = False
            
            # Get all groups
            user_groups = user.groups.all()
            
            # Loop the groups
            for group in user_groups:
                if (group.id == settings.COMMON_GROUP_ID):
                    is_already_member = True
                    break
            
            # The user is not already a member, add
            if (is_already_member == False):
                # Logging
                logger.info("User id " + str(user.id) + " is not a member of the common group, adding.")
                
                # Adding to group
                COMMON_GROUP_OBJ.user_set.add(user)
                
                # Increase counter
                synces += 1
        
        # Logging the result
        logger.info("Added " + str(synces) + " users to the common group.")
    

schedule.register(SynchronizeBedFagUsers, day_of_week='mon-sun', hour=4, minute=00)