# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand

# Define the ids for all the groups
BEDKOM_GROUP_ID = 2
FAGKOM_GROUP_ID = 3
COMMON_GROUP_ID = 4

class Command(NoArgsCommand):
	help = u'Alle medlemmer av bedKom og fagKom blir automatisk medlem av en felles gruppe om de ikke allerede er i den gruppen'

	def handle_noargs(self, **options):
		from django.contrib.auth.models import Group
		from apps.authentication.models import OnlineUser as User

		# Define container for all users
		user_container = []

		# Get bedKom-group
		bedkom_group = Group.objects.get(id = BEDKOM_GROUP_ID)

		# Append bedKom to dict
		for user in bedkom_group.user_set.all():
			user_container.append(user)

		# Get fagKom group
		fagkom_group = Group.objects.get(id = FAGKOM_GROUP_ID)

		# Append fagKom to dict if user is not already there
		for user in fagkom_group.user_set.all():
			found = False
			for existing_user in user_container:
				if (user.id == existing_user.id):
					found = True
					break

			if (found == False):
				user_container.append(user)

		# Load object for the common group
		COMMON_GROUP_OBJ = Group.objects.get(id = COMMON_GROUP_ID)

		# Loop the list of all users we have by now
		for user in user_container:
			is_already_member = False

			# Get all groups
			user_groups = user.groups.all()
			
			# Loop the groups
			for group in user_groups:
				if (group.id == COMMON_GROUP_ID):
					is_already_member = True
					break
			
			# The user is not already a member, add
			if (is_already_member == False):
				COMMON_GROUP_OBJ.user_set.add(user)