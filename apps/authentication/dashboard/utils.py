import json

from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404

from apps.authentication.models import GroupMember, GroupRole, OnlineGroup
from apps.authentication.models import OnlineUser as User


def get_base_action_context(group: OnlineGroup):
    context = {"status": 200}
    members = []
    for member in group.members.all().order_by("user__first_name", "user__last_name"):
        members.append(
            {
                "id": member.id,
                "user_id": member.user.id,
                "full_name": member.user.get_full_name(),
                "is_retired": member.is_retired,
                "is_on_leave": member.is_on_leave,
                "roles": [
                    {"id": role.id, "verbose_name": role.verbose_name}
                    for role in member.roles.all()
                ],
            }
        )
    context["members"] = members
    context["group_roles"] = [
        {"id": role.id, "verbose_name": role.verbose_name} for role in group.roles.all()
    ]
    return context


def handle_group_member_remove(
    request: HttpRequest, group: OnlineGroup
) -> HttpResponse:
    user = get_object_or_404(User, pk=int(request.POST["user_id"]))
    member = get_object_or_404(GroupMember, user=user, group=group)
    member.delete()

    context = get_base_action_context(group)
    message = f"{user.get_full_name()} ble fjernet fra {group.name_long}"
    context["message"] = message
    return HttpResponse(json.dumps(context), status=200)


def handle_group_member_add(request: HttpRequest, group: OnlineGroup) -> HttpResponse:
    user = get_object_or_404(User, pk=int(request.POST["user_id"]))
    full_name = user.get_full_name()
    try:
        group.add_user(user)
        context = get_base_action_context(group)
        context["full_name"] = full_name
        context["message"] = f"{full_name} ble lagt til i {group.name_long}"

        return HttpResponse(json.dumps(context), status=200)
    except IntegrityError:
        return HttpResponse(
            f"{full_name} er allerede i gruppen {group.name_long}", status=400
        )


def handle_group_role_add(request: HttpRequest, group: OnlineGroup) -> HttpResponse:
    user_id = int(request.POST["user_id"])
    role_id = int(request.POST["role_id"])
    user = get_object_or_404(User, pk=user_id)
    member = get_object_or_404(GroupMember, user=user, group=group)
    role = get_object_or_404(GroupRole, pk=role_id)
    if member.roles.filter(pk=role.id).exists():
        return HttpResponse(
            f"{user.get_full_name()} har allerde rollen {role.verbose_name}", status=400
        )
    member.roles.add(role)

    context = get_base_action_context(group)
    message = f"{user.get_full_name()} fikk rollen {role.verbose_name}"
    context["message"] = message

    return HttpResponse(json.dumps(context), status=200)


def handle_group_role_remove(request: HttpRequest, group: OnlineGroup) -> HttpResponse:
    user_id = int(request.POST["user_id"])
    role_id = int(request.POST["role_id"])
    user = get_object_or_404(User, pk=user_id)
    member = get_object_or_404(GroupMember, user=user, group=group)
    role = get_object_or_404(GroupRole, pk=role_id)
    if not member.roles.filter(pk=role.id).exists():
        return HttpResponse(
            f"{user.get_full_name()} har ikke rollen {role.verbose_name}", status=400
        )
    member.roles.remove(role)

    context = get_base_action_context(group)
    message = f"Rollen {role.verbose_name} ble fjernet fra {user.get_full_name()}"
    context["message"] = message

    return HttpResponse(json.dumps(context), status=200)
