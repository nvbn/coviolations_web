class covio_redis {
  package {'redis-server':
    ensure => installed,
  }

  service {'redis-server':
    ensure => running,
    enable => true,
    require => Package['redis-server'],
  }
}
