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
        logger = logging.getLogger('syncer')
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


class SynchronizePublicWikiEditAccess(Task):

    @staticmethod
    def run():
        logger = logging.getLogger('syncer')
        locale.setlocale(locale.LC_ALL, "en_US.utf8")
        
        SynchronizePublicWikiEditAccess.sync_users(logger)
    
    @staticmethod
    def sync_users(logger):
        # Logging
        logger.info("Started syncing users to a common group for edit access of open wiki")
        
        # Define container for all users
        user_container = []
        
        for group_id in settings.WIKI_OPEN_EDIT_ACCESS:
            # Get users for this group
            group_members = Group.objects.get(id = group_id)
            
            # Append users to user_container (if they are not already there)
            for user in group_members.user_set.all():
                if user not in user_container:
                    user_container.append(user)
        
        # Load object for the group the users should be assigned to
        WIKI_EDIT_ACCESS_GROUP = Group.objects.get(id = settings.WIKI_OPEN_EDIT_ACCESS_GROUP_ID)
        
        # Loop the list of all users we have
        for user in user_container:
            is_already_member = False
            
            # Get all groups
            user_groups = user.groups.all()
            
            # Loop the groups
            for group in user_groups:
                if (group.id == settings.WIKI_OPEN_EDIT_ACCESS_GROUP_ID):
                    is_already_member = True
                    break
            
            # The user is not already a member, add
            if (is_already_member == False):
                # Logging
                logger.info("User id " + str(user.id) + " is not a member of the group having " \
                            "public wiki edit permissions. Adding.")
                
                # Adding to group
                WIKI_EDIT_ACCESS_GROUP.user_set.add(user)


class SynchronizeCommitteeAccess(Task):

    @staticmethod
    def run():
        logger = logging.getLogger('syncer')
        locale.setlocale(locale.LC_ALL, "en_US.utf8")
        
        SynchronizeCommitteeAccess.sync_users(logger)
    
    @staticmethod
    def sync_users(logger):
        # Logging
        logger.info("Started syncing users to a common group for committee access")
        
        # Define container for all users
        user_container = []
        
        for group_id in settings.WIKI_COMMITTEE_ACCESS:
            # Get users for this group
            group_members = Group.objects.get(id = group_id)
            
            # Append users to user_container (if they are not already there)
            for user in group_members.user_set.all():
                if user not in user_container:
                    user_container.append(user)
        
        # Load object for the group the users should be assigned to
        WIKI_COMMITTEE_GROUP = Group.objects.get(id = settings.WIKI_COMMITTEE_ACCESS_GROUP_ID)
        
        # Loop the list of all users we have
        for user in user_container:
            is_already_member = False
            
            # Get all groups
            user_groups = user.groups.all()
            
            # Loop the groups
            for group in user_groups:
                if (group.id == settings.WIKI_COMMITTEE_ACCESS_GROUP_ID):
                    is_already_member = True
                    break
            
            # The user is not already a member, add
            if (is_already_member == False):
                # Logging
                logger.info("User id " + str(user.id) + " is not a member of the group having " \
                            "access permissions to the committee wiki. Adding.")
                
                # Adding to group
                WIKI_COMMITTEE_GROUP.user_set.add(user)

schedule.register(SynchronizeBedFagUsers, day_of_week='mon-sun', hour=4, minute=00)
schedule.register(SynchronizePublicWikiEditAccess, day_of_week='mon-sun', hour=4, minute=00)
schedule.register(SynchronizeCommitteeAccess, day_of_week='mon-sun', hour=4, minute=00)