# -*- encoding: utf-8 -*-

from logging import getLogger

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from guardian.decorators import permission_required

from apps.dashboard.tools import get_base_context, has_access
from apps.inventory.dashboard.forms import BatchForm, CategoryForm, ItemForm
from apps.inventory.models import Batch, Item, ItemCategory
from apps.shop.models import Order


@login_required
@permission_required('inventory.view_item', return_403=True)
def index(request):

    # Generic check to see if user has access to dashboard. (In Komiteer or superuser)
    if not has_access(request):
        raise PermissionDenied

    # Create the base context needed for the sidebar
    context = get_base_context(request)

    context['items'] = Item.objects.all().order_by('name')

    return render(request, 'inventory/dashboard/index.html', context)


@login_required
@permission_required('inventory.add_item', return_403=True)
def new(request):

    if not has_access(request):
        raise PermissionDenied

    # Get base context
    context = get_base_context(request)

    if request.method == 'POST':
        inventory_form = ItemForm(request.POST)

        if not inventory_form.is_valid():
            messages.error(request, 'Noen av de påkrevde feltene inneholder feil.')
        else:
            item = inventory_form.save()
            messages.success(request, 'Varen ble opprettet')
            return redirect(details, item.id)

        context['form'] = inventory_form

    else:
        context['form'] = ItemForm()

    return render(request, 'inventory/dashboard/new.html', context)


@login_required
@permission_required('inventory.view_item', return_403=True)
def details(request, item_pk):
    # Generic check to see if user has access to dashboard. (In Komiteer or superuser)
    if not has_access(request):
        raise PermissionDenied

    # Create the base context needed for the sidebar
    context = get_base_context(request)

    context['item'] = get_object_or_404(Item, pk=item_pk)

    if request.method == 'POST':
        if 'inventory.change_item' not in context['user_permissions']:
            raise PermissionDenied

        item_form = ItemForm(request.POST, instance=context['item'])
        if not item_form.is_valid():
            messages.error(request, 'Noen av de påkrevde feltene inneholder feil.')
        else:
            item_form.save()
            messages.success(request, 'Varen ble oppdatert')
        context['form'] = item_form
    else:
        context['form'] = ItemForm(instance=context['item'])

    context['new_batch_form'] = BatchForm()

    context['batch_forms'] = [
        (b.id, BatchForm(instance=b)) for b in Batch.objects.filter(item=context['item'])
    ]

    return render(request, 'inventory/dashboard/details.html', context)


@login_required
@permission_required('inventory.delete_item', return_403=True)
def item_delete(request, item_pk):
    if not has_access(request):
        raise PermissionDenied

    item = get_object_or_404(Item, pk=item_pk)

    if request.method == 'POST':

        item.delete()

        messages.success(request, 'Varen %s ble slettet.' % item.name)

        return redirect(index)

    raise PermissionDenied


@login_required
@permission_required('inventory.add_batch', return_403=True)
def batch_new(request, item_pk):
    if not has_access(request):
        raise PermissionDenied

    # Field mapper
    fieldmap = {
        'amount': 'Mengde',
        'expiration_date': 'Utløpsdato',
    }

    item = get_object_or_404(Item, pk=item_pk)

    if request.method == 'POST':
        batch_form = BatchForm(request.POST)

        if not batch_form.is_valid():
            # Dirty hack to display errors since the form is not passed in redirect context
            error_reply = "Feil i felt:"
            for field, error in batch_form.errors.items():
                error_reply += ' ' + fieldmap[field] + ' (' + batch_form.error_class.as_text(error) + '),'

            messages.error(request, error_reply.rstrip(','))
        else:
            b = batch_form.save(commit=False)
            b.item = item
            b.save()
            messages.success(request, 'Batchen ble lagt til.')

        return redirect(details, item_pk=item_pk)

    raise PermissionDenied


@login_required
@permission_required('inventory.change_batch', return_403=True)
def batch(request, item_pk, batch_pk):
    if not has_access(request):
        raise PermissionDenied

    # Get base context

    get_object_or_404(Item, pk=item_pk)
    b = get_object_or_404(Batch, pk=batch_pk)

    if request.method == 'POST':
        batch_form = BatchForm(request.POST, instance=b)

        if not batch_form.is_valid():
            messages.error(request, 'Noen av de påkrevde feltene inneholder feil.')
        else:
            batch_form.save()
            messages.success(request, 'Batchen ble oppdatert.')

        return redirect(details, item_pk=item_pk)

    raise PermissionDenied


@login_required
@permission_required('inventory.delete_batch', return_403=True)
def batch_delete(request, item_pk, batch_pk):
    if not has_access(request):
        raise PermissionDenied

    b = get_object_or_404(Batch, pk=batch_pk)

    if request.method == 'POST':

        b.delete()
        messages.success(request, 'Batchen ble slettet.')

        return redirect(details, item_pk=item_pk)

    raise PermissionDenied


@login_required
@permission_required('inventory.view_itemcategory', return_403=True)
def category_index(request):

    # Generic check to see if user has access to dashboard. (In Komiteer or superuser)
    if not has_access(request):
        raise PermissionDenied

    # Create the base context needed for the sidebar
    context = get_base_context(request)

    context['categories'] = ItemCategory.objects.all()

    return render(request, 'inventory/dashboard/category_index.html', context)


@login_required
@permission_required('inventory.view_itemcategory', return_403=True)
def category_details(request, category_pk):
    # Generic check to see if user has access to dashboard. (In Komiteer or superuser)
    if not has_access(request):
        raise PermissionDenied

    # Create the base context needed for the sidebar
    context = get_base_context(request)

    context['category'] = get_object_or_404(ItemCategory, pk=category_pk)

    if request.method == 'POST':

        form = CategoryForm(request.POST, instance=context['category'])
        if not form.is_valid():
            messages.error(request, 'Noen av de påkrevde feltene inneholder feil.')
        else:
            form.save()
            messages.success(request, 'Kategorien ble oppdatert')
            return redirect(category_index)

        context['form'] = form
    else:
        context['form'] = CategoryForm(instance=context['category'])

    return render(request, 'inventory/dashboard/category_new.html', context)


@login_required
@permission_required('inventory.add_itemcategory', return_403=True)
def category_new(request):

    if not has_access(request):
        raise PermissionDenied

    # Get base context
    context = get_base_context(request)

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if not form.is_valid():
            messages.error(request, 'Noen av de påkrevde feltene inneholder feil.')
        else:
            form.save()
            messages.success(request, 'Kategorien ble opprettet')
            return redirect(category_index)

        context['form'] = form
    else:
        context['form'] = CategoryForm()

    return render(request, 'inventory/dashboard/category_new.html', context)


@login_required
@permission_required('inventory.delete_itemcategory', return_403=True)
def category_delete(request, category_pk):
    if not has_access(request):
        raise PermissionDenied

    category = get_object_or_404(ItemCategory, pk=category_pk)

    items = Item.objects.filter(category=category)

    # Removes the category binding to prevent cascading delete
    for item in items:
        item.category = None
        item.save()

    category.delete()
    messages.success(request, 'Kategorien %s ble slettet.' % category.name)
    return redirect(category_index)

    raise PermissionDenied


@login_required
# @permission_required('inventory.delete_batch', return_403=True)
def statistics(request):
    # if not has_access(request):
    #     raise PermissionDenied

    context = get_base_context(request)

    return render(request, 'inventory/dashboard/statistics.html', context)


@login_required
def order_statistics(request):
    # TODO check permissions

    statistics = dict()

    counts = Order.objects.all().values('object_id', 'content_type').annotate(total=Count('object_id'))
    item_type = ContentType.objects.get_for_model(Item)

    for count in counts:
        print(count)
        if item_type.id == count['content_type']:
            try:
                item = Item.objects.get(pk=count['object_id'])
            except Item.DoesNotExist:
                getLogger(__name__).error('Item with pk %s does not exist (DoesNotExist error)' % count['object_id'])
            except KeyError:
                getLogger(__name__).error('Key "object_id" does not exist')
            if count['total'] > 0:
                statistics[item.name] = count['total']

    return JsonResponse(statistics)
