Exec {
  path => "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
}

class {'apt':
  always_apt_update => true,
}

import "private.pp"
import "mongo.pp"
import "nodejs.pp"
import "ruby.pp"
import "python.pp"
import "supervisor.pp"
import "nginx.pp"
import "postgresql.pp"
import "redis.pp"
import "project.pp"

include covio_python
include covio_nodejs
include covio_ruby
include covio_mongo
include covio_postgresql
include covio_redis

class {"covio_project":
  require => [
    Class['covio_python'],
    Class['covio_nodejs'],
    Class['covio_ruby'],
    Class['covio_mongo'],
    Class['covio_postgresql'],
    Class['covio_redis']
  ]
}

class {"covio_supervisor":
  require => Class['covio_project'],
}
