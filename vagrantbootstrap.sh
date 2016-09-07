#!/bin/bash


LJUST_COLS=20
RJUST_COLS=30
VERBOSE=true
RUNSERVER=false


function init() {
    printf "\n\nVERBOSE = $VERBOSE, toggle in vagrantbootstrap.sh\n\n"
    sleep 1

    echo "killing running dev servers"
    pkill -9 -f "python manage.py"
}

function progress() {
    if $VERBOSE
    then
        $@
    else
        cmd="$@"
        $@ &> /dev/null &
        pid=$!
        spinner='-\|/'

        i=0
        while kill -0 $pid &> /dev/null
        do
            i=$(( (i+1) %4 ))
            printf "\r\t%-${LJUST_COLS}.${LJUST_COLS}s %${RJUST_COLS}s" "${cmd}" "[ ${spinner:$i:1}${spinner:$i:1} ]"
            sleep .1
        done

        if [ $? -ne 0 ]
        then
            echo "return code $?";
        fi
        printf "\r\t%-${LJUST_COLS}.${LJUST_COLS}s %${RJUST_COLS}s\n" "${cmd}" "[ OK ]"
    fi
}


function add_custom_repos() {
    echo "adding custom repositories for nodejs"
    progress curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -
}

function update_packages() {
    echo "updating packages"
    progress sudo apt-get update
}

function install_curl() {
    echo "installing curl"
    progress sudo apt-get install curl
}

function install_packages() {
    echo "installing packages"
    progress sudo apt-get install -y \
        python-dev python3-dev python-setuptools python-virtualenv vim \
        tmux screen git-core build-essential openssl \
        libjpeg8 libjpeg8-dev zlib-bin libtiff4-dev libfreetype6 libfreetype6-dev libpq-dev libssl-dev\
        python-psycopg2 imagemagick \
        nodejs \
        libffi-dev \
        libldap2-dev \
        libsasl2-dev \
        libssl-dev
}

function setup_virtualenv() {
    echo "installing virtualenvwrapper"
    # use pip to install globally, installing with apt doesn't create the shellscript for sourcing
    progress sudo pip install virtualenvwrapper
    source /usr/local/bin/virtualenvwrapper.sh

    if ! grep -q "source /usr/local/bin/virtualenvwrapper.sh" .bashrc; then
        echo "adding script to .bashrc"
        echo 'source /usr/local/bin/virtualenvwrapper.sh' >> ~/.bashrc
    fi

    echo "creating virtualenv"
    progress mkvirtualenv -p `which python3` onlineweb
}

function install_onlineweb_requirements() {
    echo "installing onlineweb requirements"
    workon onlineweb
    cd /vagrant
    progress pip install -U -r requirements.txt
}

function install_lessc() {
    progress sudo npm install less -g
}

function prepare_and_run_onlineweb() {
    workon onlineweb
    cd /vagrant
    cp onlineweb4/settings/example-local.py onlineweb4/settings/local.py
    echo "creating tables"
    progress python manage.py migrate
    if $RUNSERVER
    then
        echo "starting dev server"
        python manage.py runserver 0.0.0.0:8000 &
        echo "done, check http://localhost:8001 on host"
    fi
}

init
update_packages
install_curl
add_custom_repos
update_packages
install_packages
setup_virtualenv
install_onlineweb_requirements
install_lessc
prepare_and_run_onlineweb

# Support for pip install inside the VM
curl https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py | python
