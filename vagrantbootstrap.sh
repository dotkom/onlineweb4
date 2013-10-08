#!/bin/bash


LJUST_COLS=20
RJUST_COLS=30
VERBOSE=false


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

function update_packages() {
    echo "updating packages"
    progress sudo apt-get update
}

function install_packages() {
    echo "installing packages"
    progress sudo apt-get install -y \
        python-dev python-setuptools python-virtualenv vim \
        tmux screen git-core curl build-essential openssl \
        libjpeg8 libjpeg8-dev zlib-bin libtiff4 libtiff4-dev libfreetype6 libfreetype6-dev libwebp2 libpq-dev libssl-dev\
        python-psycopg2
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
    progress mkvirtualenv onlineweb
}

function install_onlineweb_requirements() {
    echo "installing onlineweb requirements"
    workon onlineweb
    cd /vagrant
    progress pip install -r requirements.txt
}


function install_lessc() {
    cd /home/vagrant
    workon onlineweb
    echo "installing node"
    if [ ! -f "node-v0.10.20.tar.gz" ]
    then
        if $VERBOSE
        then
            progress wget http://nodejs.org/dist/v0.10.20/node-v0.10.20.tar.gz
        else
            progress wget --quiet http://nodejs.org/dist/v0.10.20/node-v0.10.20.tar.gz
        fi
    fi
    progress tar zxf node-v0.10.20.tar.gz
    cd node-v0.10.20/
    # set install prefix to virtualenv directory, maybe this will solve the problems with lessc not being available in the virtualenv
    progress ./configure --prefix /home/vagrant/.virtualenvs/onlineweb/
    echo "compiling node (go get coffee)"
    progress make
    progress make install

    workon onlineweb
    if ! type "npm" > /dev/null; then
        echo "installing npm"
        progress `curl https://npmjs.org/install.sh | sh`
    fi

    echo "installing less compiler"
    progress npm install less -g
}

function prepare_and_run_onlineweb() {
    workon onlineweb
    cd /vagrant
    cp onlineweb4/settings/example-local.py onlineweb4/settings/local.py
    echo "creating tables"
    progress python manage.py syncdb
    echo "starting dev server"
    python manage.py runserver 0.0.0.0:8000 &
    echo "done, check http://localhost:8001 on host"
}

init

update_packages
install_packages
setup_virtualenv
install_onlineweb_requirements
install_lessc
prepare_and_run_onlineweb
