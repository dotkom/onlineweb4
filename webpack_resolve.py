import json
import os
import wiki

DJANGO_WIKI_STATIC = os.path.join(os.path.dirname(wiki.__file__), 'static')
WEBPACK_RESOLVE_FILE = 'webpack-extra-resolve.json'

# This whole file is essentially just a big ugly hack.
# For webpack to properly build wiki static files it needs the absolute path to the wiki
# static folder. And since we're using virtualenvs there is no easy way to find this folder
# without running python code


def create_resolve_file():
    # Write to json file which will be read by webpack
    with open(WEBPACK_RESOLVE_FILE, 'w') as f:
        f.write(json.dumps({
            'paths': [
                DJANGO_WIKI_STATIC
            ]
        }))


if __name__ == '__main__':
    # Only run if file is executed directly
    create_resolve_file()
