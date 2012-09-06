#Global assets for django
from django_assets import Bundle, register
from webassets.filter import get_filter
from django.conf import settings

scss_filter = get_filter('pyscss', debug_info=settings.SCSS_DEBUG)

scss = Bundle(
    "scss/site.scss",

    filters=scss_filter,
    output="assets/css/style.css",
    debug=False
)

register('css_site',
    Bundle(
        scss,
        filters="cssmin",
        output="assets/css/style.css"
    )
)

js = Bundle(
    "js/plugins.js",

    filters="jsmin",
    output="assets/js/onlineweb.js"
)
register("js_all", js)
