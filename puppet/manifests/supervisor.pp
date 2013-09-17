class covio_supervisor {
  include supervisor

  supervisor::service { "coviolations_web":
    ensure => present,
    enable => true,
    command => '/var/www/env/coviolations/bin/gunicorn coviolations_web.wsgi:application  -b 127.0.0.1:8102 -w 4',
    user => 'www-data',
    group => 'www-data',
    directory => '/var/www/coviolations/',
  }

  supervisor::service { "coviolations_worker":
    ensure => present,
    enable => true,
    command => '/var/www/env/coviolations/bin/python manage.py rqworker',
    user => 'www-data',
    group => 'www-data',
    directory => '/var/www/coviolations/',
  }

  supervisor::service { "coviolations_push":
    ensure => present,
    enable => true,
    command => '/var/www/env/coviolations/bin/python manage.py runpush 9102',
    user => 'www-data',
    group => 'www-data',
    directory => '/var/www/coviolations/',
  }
}
