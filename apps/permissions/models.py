from typing import Iterable

from django.contrib.auth.models import Group
from django.db import models
from guardian.shortcuts import (
    assign_perm,
    get_groups_with_perms,
    get_perms_for_model,
    get_users_with_perms,
    remove_perm,
)


class ObjectPermissionModel(models.Model):
    def get_permission_users(self):
        from apps.authentication.models import OnlineUser as User

        return User.objects.none()

    def get_permission_groups(self):
        return Group.objects.none()

    @classmethod
    def get_model_permissions(cls):
        return get_perms_for_model(cls)

    def _set_permissions(self, users: Iterable, groups: Iterable[Group]):
        permissions = self.get_model_permissions()
        for permission in permissions:
            for user in users:
                assign_perm(perm=permission, user_or_group=user, obj=self)
            for group in groups:
                assign_perm(perm=permission, user_or_group=group, obj=self)

    def _remove_permissions(self, users: Iterable, groups: Iterable[Group]):
        permissions = self.get_model_permissions()
        for permission in permissions:
            for user in users:
                remove_perm(perm=permission, user_or_group=user, obj=self)
            for group in groups:
                remove_perm(perm=permission, user_or_group=group, obj=self)

    def _get_current_permission_users(self):
        return get_users_with_perms(obj=self, with_group_users=False)

    def _get_current_permission_groups(self):
        return get_groups_with_perms(obj=self)

    def assign_permissions(self):
        current_users = self._get_current_permission_users()
        new_users = self.get_permission_users()
        removed_users = current_users.exclude(pk__in=new_users.values_list("id"))
        added_users = new_users.exclude(pk__in=current_users.values_list("id"))

        current_groups = self._get_current_permission_groups()
        new_groups = self.get_permission_groups()
        removed_groups = current_groups.exclude(pk__in=new_groups.values_list("id"))
        added_groups = new_groups.exclude(pk__in=current_groups.values_list("id"))

        self._remove_permissions(removed_users, removed_groups)
        self._set_permissions(added_users, added_groups)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.assign_permissions()

    class Meta:
        abstract = True
