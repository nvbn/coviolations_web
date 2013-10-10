from fabric.api import local, lcd, sudo, put, cd


def compile_assets():
    """Compile sass and coffee"""
    local('coffee -c . .')
    local('sass app/static/sass/style.sass app/static/sass/style.css')


def install_assets():
    """Download and build assets"""
    local('./manage.py bower_install')

    with lcd('components/bower_components/sockjs-client'):
        local('echo echo \\ | cat - version > VERSION-GEN')
        local('npm install')
        local('make build')

    with lcd('components/bower_components/google-code-prettify'):
        local('make')


def update_db():
    """Prepare database"""
    local('./manage.py syncdb --noinput')
    local('./manage.py migrate --noinput')


def install_requirements(mode='develop'):
    """Install requirements"""
    local('pip install -U -r requirements/{}.txt'.format(mode))


def collect_static():
    """Collect static"""
    local('./manage.py collectstatic --noinput')


def install(mode='develop'):
    """Install project"""
    install_requirements(mode)
    if mode != 'ci':
        install_assets()
        compile_assets()
    update_db()
    if mode == 'production':
        collect_static()


update = install


def prepare_server(branch='master'):
    """Prepare server"""
    sudo('wget http://apt.puppetlabs.com/puppetlabs-release-precise.deb')
    sudo('dpkg -i puppetlabs-release-precise.deb')
    sudo('apt-get update -qq')
    sudo('apt-get install puppet -qq')
    sudo('mkdir /var/www/coviolations -p')
    sudo('apt-get install git-core -qq')
    sudo('chown -R www-data /var/www/coviolations')
    with cd('/var/www/coviolations'):
        sudo(
            'git clone https://github.com/nvbn/coviolations_web.git '
            '--recursive .', user='www-data',
        )
        sudo('git checkout {}'.format(branch), user='www-data')
        sudo('git submodule init')
        sudo('git submodule update')
        put(
            'puppet/manifests/private.pp', 'puppet/manifests/private.pp',
            use_sudo=True,
        )
        sudo('chown www-data puppet/manifests/private.pp')
        sudo('puppet apply puppet/manifests/site.pp'
             ' --modulepath=puppet/modules/')


def update_server(branch='master'):
    """Update server"""
    with cd('/var/www/coviolations'):
        sudo('git checkout {}'.format(branch), user='www-data')
        sudo('git submodule update')
        put(
            'puppet/manifests/private.pp', 'puppet/manifests/private.pp',
            use_sudo=True,
        )
        sudo('chown www-data puppet/manifests/private.pp')
        sudo('puppet apply puppet/manifests/site.pp'
             ' --modulepath=puppet/modules/')


def test_client():
    """Test client with testem"""
    local('./manage.py collectstatic --noinput')
    local('mkdir -p client_tests')
    local('cp static_collected -a client_tests/static')
    local('cp static/tests/testem.yml client_tests')
    with lcd('client_tests'):
        local('testem')
        local('rm -rf *')
