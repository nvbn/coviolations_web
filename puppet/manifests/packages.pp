package {'nginx':
  ensure => latest,
}

package {'redis-server':
  ensure => installed,
}

package {'postgresql':
  ensure => installed,
}

package {'postgresql-server-dev-all':
  ensure => installed,
}
