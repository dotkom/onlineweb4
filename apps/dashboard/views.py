# -*- encoding: utf-8 -*-

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required

@permission_required('dashboard.main')
def index(request):
    """
    This is the main dashboard view
    """

    return render(request, 'dashboard.html', {})

def _create_permissions_dictionary(request):
    """
    Helper method to create a complete dictionary of permissions
    and model managers needed to render the dashboard_base template
    """
    
    pass   
