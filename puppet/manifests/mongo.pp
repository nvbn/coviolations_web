apt::source { 'mongodb':
  location  => 'http://downloads-distro.mongodb.org/repo/ubuntu-upstart',
  repos => '10gen',
  release => 'dist',
  key => '7F0CEB10',
  key_server => 'hkp://keyserver.ubuntu.com:80',
  include_src => false,
  notify => Package['mongodb-10gen'],
}

package {'mongodb-server':
  ensure => absent,
}

package {'mongodb-clients':
  ensure => absent,
}

package {'mongodb-10gen':
  ensure => latest,
  require => [
    Package['mongodb-server'],
    Package['mongodb-clients']
  ]
}
