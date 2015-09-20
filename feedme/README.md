Pizzasystem
===========

Pizza ordering managing

Install:
1. Add "feedme" to your INSTALLED_APPS setting like this:

      INSTALLED_APPS = (
          ...
          'feedme',
      )

2. Add the following to settings:

      FEEDME_GROUP = 'dotkom'

      FEEDME_ADMIN_GROUP = 'feedmeadmin'

3. Include the feedme URLconf in your project urls.py like this:

      url(r'^feedme/', include('feedme.urls')),

4. Run `python manage.py syncdb` to create the feedme models.

5. Visit http://127.0.0.1:8000/feedme/

**Remember to update version number in setup.py before making a new release!**
