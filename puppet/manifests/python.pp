class covio_python {
  file {'/var/www/env':
    ensure => "directory",
    owner => www-data,
  }

  class {"python::venv":
    owner => "www-data",
  }

  python::venv::isolate { "/var/www/env/coviolations":
    version => '2.7',
    requirements => "/var/www/coviolations/requirements/production.txt",
    require => [
      Package['postgresql-server-dev-all'],
      File['/var/www/env']
    ],
  }
}
