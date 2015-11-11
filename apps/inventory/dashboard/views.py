# -*- encoding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect

from guardian.decorators import permission_required

from apps.dashboard.tools import has_access, get_base_context
from apps.inventory.dashboard.forms import ItemForm, BatchForm
from apps.inventory.models import Item, Batch


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
            messages.error(request, u'Noen av de påkrevde feltene inneholder feil.')
        else:
            item = inventory_form.save()
            messages.success(request, u'Varen ble opprettet')
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
            messages.error(request, u'Noen av de påkrevde feltene inneholder feil.')
        else:
            item_form.save()
            messages.success(request, u'Varen ble oppdatert')
        context['item_form'] = item_form
    else:
        context['item_form'] = ItemForm(instance=context['item'])

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

        messages.success(request, u'Varen %s ble slettet.' % item.name)

        return redirect(index)

    raise PermissionDenied


@login_required
@permission_required('inventory.add_batch', return_403=True)
def batch_new(request, item_pk):
    if not has_access(request):
        raise PermissionDenied

    # Field mapper
    fieldmap = {
        'amount': u'Mengde',
        'expiration_date': u'Utløpsdato',
    }

    item = get_object_or_404(Item, pk=item_pk)

    if request.method == 'POST':
        batch_form = BatchForm(request.POST)

        if not batch_form.is_valid():
            # Dirty hack to display errors since the form is not passed in redirect context
            error_reply = u"Feil i felt:"
            for field, error in batch_form.errors.items():
                error_reply += ' ' + fieldmap[field] + ' (' + batch_form.error_class.as_text(error) + '),'

            messages.error(request, error_reply.rstrip(','))
        else:
            b = batch_form.save(commit=False)
            b.item = item
            b.save()
            messages.success(request, u'Batchen ble lagt til.')

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
            messages.error(request, u'Noen av de påkrevde feltene inneholder feil.')
        else:
            batch_form.save()
            messages.success(request, u'Batchen ble oppdatert.')

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
        messages.success(request, u'Batchen ble slettet.')

        return redirect(details, item_pk=item_pk)

    raise PermissionDenied
