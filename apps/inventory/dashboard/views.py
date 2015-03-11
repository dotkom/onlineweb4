# -*- encoding: utf-8 -*-

from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse

from guardian.decorators import permission_required

from apps.dashboard.tools import has_access, get_base_context
from apps.inventory.dashboard.forms import InventoryForm, BatchForm
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
        inventory_form = InventoryForm(request.POST)

        if not inventory_form.is_valid():
            messages.error(request, u'Noen av de påkrevde feltene inneholder feil.')
        else:
            inventory_form.save()
            messages.success(request, u'Varen ble opprettet')
            return redirect(index)

        context['form'] = inventory_form

    else:
        context['form'] = InventoryForm()

    return render(request, 'inventory/dashboard/new.html', context)


@login_required
@permission_required('inventory.view_item', return_403=True)
def details(request, pk):
    # Generic check to see if user has access to dashboard. (In Komiteer or superuser)
    if not has_access(request):
        raise PermissionDenied

    # Create the base context needed for the sidebar
    context = get_base_context(request)

    context['item'] = get_object_or_404(Item, pk=pk)

    if request.method == 'POST':
        if 'inventory.change_item' not in context['user_permissions']:
            raise PermissionDenied

        inventory_form = InventoryForm(request.POST, instance=context['item'])
        if not inventory_form.is_valid():
            messages.error(request, u'Noen av de påkrevde feltene inneholder feil.')
        else:
            inventory_form.save()
            messages.success(request, u'Varen ble oppdatert')
        context['form'] = inventory_form
    else:
        context['form'] = InventoryForm(instance=context['item'])

    return render(request, 'inventory/dashboard/details.html', context)

@login_required
@permission_required('inventory.delete_item', return_403=True)
def delete(request, pk):
    if not has_access(request):
        raise PermissionDenied

    # Get base context needed for sidebar, and permissions
    context = get_base_context(request)

    context['item'] = get_object_or_404(Item, pk=pk)

    messages.success(request, u'Varen %s ble slettet.' % context['item'].name)

    context['item'].delete()

    return redirect(index)

@login_required
@permission_required('inventory.add_batch', return_403=True)
def batch(request, pk):
    if not has_access(request):
        raise PermissionDenied

    # Get base context

    item = get_object_or_404(Item, pk=pk)

    if request.method == 'POST':
        if request.is_ajax and 'action' in request.POST:
            if request.POST['action'] == 'add':
                if 'amount' not in request.POST:
                    return HttpResponse(u'Du må spesifisere en gyldig mengde', status=400)
                else:
                    try:
                        amount =  int(request.POST['amount'])
                        if amount < 0:
                            return HttpResponse(u'Mengde kan ikke være negativ', status=400)
                        expiry = request.POST['expiry']
                        if 'expiry' in request.POST:
                            expiry = datetime.strptime(expiry, '%Y-%m-%d')
                    except ValueError:
                        return HttpResponse(u'Ugyldig format.', status=400)

                    if 'expiry' in request.POST:
                        batch = Batch(amount=amount, expiration_date=expiry.date(), item=item)
                    else:
                        batch = Batch(amount=amount, item=item)

                    batch.save()

                    return JsonResponse({'id': batch.id, 'amount': batch.amount, 'expiry': batch.expiration_date}, status=200)

            if request.POST['action'] == 'delete':
                batch = get_object_or_404(Batch, pk=request.POST['id'])
                batch.delete()
                return HttpResponse(u'Batchen ble slettet')

    raise PermissionDenied
