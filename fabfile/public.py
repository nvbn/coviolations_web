from fabric.api import local, lcd


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


def install(mode='develop'):
    """Install project"""
    install_requirements(mode)
    if mode != 'ci':
        install_assets()
        compile_assets()
    update_db()
    if mode == 'production':
        local('./manage.py collectstatic --noinput')


update = install
