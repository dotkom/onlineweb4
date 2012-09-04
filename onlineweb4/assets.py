#Global assets for django
from django_assets import Bundle, register

js = Bundle(
    "js/plugins.js",

    filters="jsmin",
    output="assets/js/onlineweb.js"
)
register("js_all", js)

scss = Bundle(
    "scss/site.scss",

    filters="pyscss",
    output="assets/css/scss.css",
    debug=False  # NEVER ignore this step
)

register('css_site',
    Bundle(
        # some other css files can be added here
        scss,
        filters="cssmin",
        output="assets/css/style.css"
    )
)
