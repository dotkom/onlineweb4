from django.conf import settings
from django.http import HttpResponseForbidden
from django.template import RequestContext,Template,loader,TemplateDoesNotExist
from importlib import import_module

"""
# Middleware to allow the display of a 403.html template when a
# 403 error is raised.
"""


class Http403(Exception):
    pass


class Http403Middleware(object):
    def process_exception(self, request, exception):
        from .http import Http403

        if not isinstance(exception, Http403):
            # Return None so django doesn't re-raise the exception
            return None

        try:
            # Handle import error but allow any type error from view
            callback = getattr(import_module(settings.ROOT_URLCONF),'handler403')
            return callback(request,exception)
        except (ImportError,AttributeError):
            # Try to get a 403 template
            try:
                # First look for a user-defined template named "403.html"
                t = loader.get_template('403.html')
            except TemplateDoesNotExist:
                # If a template doesn't exist in the projct, use the following hardcoded template
                t = Template("""{% load i18n %}
                 <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
                        "http://www.w3.org/TR/html4/strict.dtd">
                 <html>
                 <head>
                     <title>{% trans "403 ERROR: Access denied" %}</title>
                 </head>
                 <body>
                     <h1>{% trans "Access Denied (403)" %}</h1>
                     {% trans "We're sorry, but you are not authorized to view this page." %}
                 </body>
                 </html>""")

            # Now use context and render template
            c = RequestContext(request, {
                'message': exception
            })

            return HttpResponseForbidden(t.render(c))
