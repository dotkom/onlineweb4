# -*- encoding: utf-8 -*-

from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from guardian.decorators import permission_required

from apps.companyprofile.dashboard.forms import CompanyForm
from apps.companyprofile.models import Company
from apps.dashboard.tools import has_access, get_base_context


@login_required
@permission_required('companyprofile.view_company')
def index(request):
    """
    This is the main companyprofile dashboard view
    """

    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    context['companies'] = Company.objects.all().order_by('name')

    return render(request, 'company/dashboard/index.html', context)


# GROUP MODULE VIEWS
@login_required
@permission_required('companyprofile.add_company')
def new(request):
    """
    Create new companyprofile
    """

    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    if request.method == 'POST':
        company_form = CompanyForm(request.POST)
        if not company_form.is_valid():
            messages.error(request, 'Noen av de påkrevde feltene inneholder feil.')
        else:
            company_form.save()
            messages.success(request, 'Bedriften ble opprettet.')

            return redirect(index)

        context['form'] = company_form
    else:
        context['form'] = CompanyForm()

    return render(request, 'company/dashboard/new.html', context)


@login_required
@permission_required('companyprofile.view_company')
def detail(request, pk):
    """
    Detailed company view per PK
    """

    if not has_access(request):
        raise PermissionDenied

    context = get_base_context(request)

    context['company'] = get_object_or_404(Company, pk=pk)

    if request.method == 'POST':
        company_form = CompanyForm(request.POST, instance=context['company'])
        if not company_form.is_valid():
            messages.error(request, 'Noen av de påkrevde feltene inneholder feil.')
        else:
            company_form.save()
            messages.success(request, 'Bedriften ble oppdatert.')
        context['form'] = company_form
    else:
        context['form'] = CompanyForm(instance=context['company'])

    return render(request, 'company/dashboard/detail.html', context)


@login_required
@permission_required('companyprofile.delete_company')
def delete(request, pk):
    """
    Deletes the Company associated with the provided primary key
    :param request: Django request object
    :param pk: The Primary Key of the company
    :return: An HttpResponse
    """

    context = get_base_context(request)

    context['company'] = get_object_or_404(Company, pk=pk)

    if request.method == 'POST':
        context['company'].delete()
        return redirect(index)

    raise PermissionDenied
