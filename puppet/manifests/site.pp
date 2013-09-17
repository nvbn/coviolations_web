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
import "packages.pp"
import "postgresql.pp"
