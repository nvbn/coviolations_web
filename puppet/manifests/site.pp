Exec {
  path => "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
}

class {'apt':
  always_apt_update => true,
}

import "mongo.pp"
import "nodejs.pp"
import "ruby.pp"

import "supervisor.pp"

import "packages.pp"
import "python.pp"
