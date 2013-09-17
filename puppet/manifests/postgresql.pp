package {'postgresql':
  ensure => installed,
}

package {'postgresql-server-dev-all':
  ensure => installed,
}
