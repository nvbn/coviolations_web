class covio_postgresql {
  package {'postgresql':
    ensure => installed,
  }

  package {'postgresql-server-dev-all':
    ensure => installed,
  }

  class {'postgresql::server': }

  postgresql::db { 'coviolations':
    owner => $db_owner,
    password => $db_password,
  }
}
