package {"openjdk-7-jdk":
  ensure => "installed"
}

exec {'retrieve_leiningen':
  command => "/usr/bin/wget -q https://raw.github.com/technomancy/leiningen/stable/bin/lein -O /usr/bin/lein",
  creates => "/usr/bin/lein",
  require => Package["openjdk-7-jdk"]
}

file {'/usr/bin/lein':
  mode => 0755,
  require => Exec["retrieve_leiningen"]
}

class {'apt':
  always_apt_update => true,
  update_timeout => 0
}

apt::ppa {"ppa:chris-lea/node.js": }

package {"nodejs":
  ensure => "installed",
  require => Apt::Ppa["ppa:chris-lea/node.js"]
}

package {'jasmine-core':
  ensure   => 'installed',
  provider => 'npm',
  require => Package["nodejs"]
}
