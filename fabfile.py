import time
import getpass
from fabric.api import cd, sudo, prompt, env, task, local, get, settings, abort
from fabric.colors import yellow, red, green
from fabric.contrib.console import confirm
 
from fabric.contrib import django
 
django.settings_module('onlineweb4.settings')
from django.conf import settings as django_settings
 
class Site(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
 
    def run(self, cmd):
        with cd(self.dir):
            sudo(cmd, user=self.user_id)
 
    def deploy(self, branch="develop", mode='full'):
        """
        Mode can be 'full' or 'quick', quick does not update packages,
        run syncdb or migrate, saves some time
        """
        self.git_pull(branch)
 
        if mode != 'quick':
            self.update_packages()
            self.run('cp onlineweb4/settings/example-local.py onlineweb4/settings/local.py')
            self.run('/var/www/.enviroments/onlineweb/bin/python manage.py syncdb')
            self.run('/var/www/.enviroments/onlineweb/bin/python manage.py migrate --delete-ghost-migrations')
 
        self.run('/var/www/.enviroments/onlineweb/bin/python manage.py collectstatic --noinput')
        self.restart()
        print green("Deployed %s" % DEV)
 
    def git_pull(self, branch):
        # .pyc files can create ghost behavior when .py files are deleted...
        self.run("find . -name '*.pyc' -delete")
        self.run("git fetch origin")
        self.run("git checkout " + branch)
        self.run("git reset --hard origin/" + branch)
 
#    def git_tag(self):
#        if confirm("Give new tag for this deployment?"):
#            self.run("git tag |tail -n 5")
#            tag = prompt('Gi ny tag for deploymenten: ')
#           self.run("git tag %s" % tag)
#            self.run("git push --tags && git push")
 
    def update_packages(self):
        self.run("/var/www/.enviroments/onlineweb/bin/pip install -r requirements.txt")
 
    def restart(self):
        header("Running: Restart server script: %s" % self.gunicorn)
        process_id = sudo('cat /var/run/gunicorn/%s' % self.gunicorn, user=self.user_id)
        sudo('kill -HUP %s' % process_id, user=self.user_id)
 
DEV = Site(
    dir='/var/www/onlineweb/dev/onlineweb4',
    gunicorn='dev.absint.no.pid',
    user_id='www-data'
)
 
PROD = Site(
    dir='/var/www/websites/www/',
    gunicorn='www.uka.no.pid',
    user_id='uka-data'
)
 
STAGING = Site(
    dir='/var/www/websites/staging/',
    gunicorn='staging.uka.no.pid',
    user_id='www-data'
)
 
env.hosts = django_settings.FAB_HOST
 
 
@task
def clone_prod_data():
    """
    Download production data (database and uploaded files) and insert locally
    """
 
    env.user = prompt('Username: ', default=getpass.getuser())
    dump_file = str(time.time()) + ".json"
 
    # Ignore errors on these next steps, so that we are sure we clean up no matter what
    with settings(warn_only=True):
        # Dump the database to a file...
        PROD.run('source venv/bin/activate && nice python manage.py dumpdata --all --exclude ' +
                 'watson --exclude event > ' + dump_file)
 
        # The download that file, and all uno's uploaded files, and cleanup the dump file
        get(PROD.dir + dump_file, dump_file)
        PROD.run('rm ' + dump_file)
        # TODO: Uncomment when we actually have an uploads dir:
        # get(PROD.dir + 'upload', 'upload/%(path)s')
 
        # Replace this db with the contents of the dump
        local('python manage.py uno-flush')
        local('python manage.py syncdb --migrate')
        local('python manage.py uno-loaddata ' + dump_file)
 
    # ... then cleanup the dump file
    local('rm ' + dump_file)
 
    # clears sorl key-value-store
    local('python manage.py thumbnail clear')
 
 
@task
def test(is_deploying=False):
    print yellow("Running tests, please wait!")
    result = local("venv/bin/python manage.py test --settings=onlineweb4.settings.test", capture=True)
    if result.failed:
        print red("Tests failed")
        if is_deploying and not confirm('Do you really want to deploy?'):
            abort('')
    else:
        print green("All tests ok")

@task
def deploy(mode='full'):
    """
    Deploy the current master branch of UNO to prod (or dev, first)
    """
    env.user = prompt('Username: ', default=getpass.getuser())
 
    if mode == 'quick':
        return PROD.deploy(mode=mode)
 
    if confirm("Run tests?"):
        test(is_deploying=True)
 
    # Check if we first want to test on dev
    if confirm("Test on DEV first?"):
        DEV.deploy(mode=mode)
        if not confirm("Deploy to staging done. Continue with deploy to production?"):
            abort('Aborting production, at your request')
 
    # Pull on the production branch
    PROD.deploy(mode=mode)
 
    #Clean static files folder
    PROD.run('rm -rf onlineweb4/static')
    PROD.run('venv/bin/python manage.py collectstatic --noinput')
    PROD.restart()
 
    #Purge all cached in varnish
    PROD.run("curl -4 -X BAN -H 'Host: www.uka.no' http://localhost:6081/")
 
    # Check if we want to tag the deployment
    PROD.git_tag()
 
@task
def purge_static(mode='full'):
    env.user = prompt('Username: ', default=getpass.getuser())
    PROD.run("curl -4 -X BAN -H 'Host: www.uka.no' http://localhost:6081/static/")
 
 
@task
def purge_all(mode='full'):
    env.user = prompt('Username: ', default=getpass.getuser())
    PROD.run("curl -4 -X BAN -H 'Host: www.uka.no' http://localhost:6081/")
 
 
@task
def deploy_branch(branch):
    """
    Deploy a branch to the test server
    """
    env.user = prompt('Username: ', default=getpass.getuser())
    DEV.deploy(branch=branch)
 
 
@task
def purge_collectstatic():
    """
    Delete static files on server and collect static
    """
    env.user = prompt('Username: ', default=getpass.getuser())
    PROD.run('rm -rf onlineweb4/static')
    PROD.run('venv/bin/python manage.py collectstatic --noinput')
    PROD.restart()
 
 
def header(text):
    print ("#" * 45) + "\n# %s\n" % text + ("#" * 45)
