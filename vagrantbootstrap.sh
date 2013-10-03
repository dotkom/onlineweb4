function update_packages() {
    echo "updating packages"
    sudo apt-get update
}

function install_packages() {
    echo "installing packages"
    sudo apt-get install -y \
        python-dev python-setuptools python-virtualenv vim \
        tmux screen git-core curl build-essential openssl \
        libjpeg8 libjpeg8-dev zlib-bin libtiff4 libtiff4-dev libfreetype6 libfreetype6-dev libwebp2 libpq-dev libssl-dev\
        python-psycopg2
}

function setup_virtualenv() {
    echo "installing virtualenvwrapper"
    # use pip to install globally, installing with apt doesn't create the shellscript for sourcing
    sudo pip install virtualenvwrapper
    source /usr/local/bin/virtualenvwrapper.sh

    if ! grep -q "source /usr/local/bin/virtualenvwrapper.sh" .bashrc; then
        echo "adding script to .bashrc"
        echo 'source /usr/local/bin/virtualenvwrapper.sh' >> ~/.bashrc
    fi

    echo "creating virtualenv"
    mkvirtualenv onlineweb
}

function install_onlineweb_requirements() {
    echo "installing onlineweb requirements"
    workon onlineweb
    cd /vagrant
    pip install -r requirements.txt
}


function install_lessc() {
    cd /home/vagrant
    workon onlineweb
    echo "installing node"
    echo "downloading node v0.10.20"
    wget http://nodejs.org/dist/v0.10.20/node-v0.10.20.tar.gz
    tar zxf node-v0.10.20.tar.gz
    cd node-v0.10.20/
    # set install prefix to virtualenv directory, maybe this will solve the problems with lessc not being available in the virtualenv
    ./configure --prefix /home/vagrant/.virtualenvs/onlineweb/

    echo "compiling in 3s (go get coffee)"
    sleep 3
    make

    echo "installing"
    make install

    echo "installing npm"
    curl https://npmjs.org/install.sh | sh

    echo "installing less compiler"
    npm install less -g
}

function prepare_and_run_onlineweb() {
    workon onlineweb
    cd /vagrant
    cp onlineweb4/settings/example-local.py onlineweb4/settings/local.py
    echo "creating tables"
    python manage.py syncdb
    echo "starting dev server"
    python manage.py runserver 0.0.0.0:8000 &
    echo "done, check http://localhost:8001 on host"
}

update_packages
install_packages
setup_virtualenv
install_onlineweb_requirements
install_lessc
prepare_and_run_onlineweb
