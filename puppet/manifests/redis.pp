class covio_redis {
  package {'redis-server':
    ensure => installed,
  }
}
