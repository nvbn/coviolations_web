apt::ppa {'ppa:chris-lea/node.js':
  notify => [Package['nodejs']],
}

package {'nodejs':
  ensure => latest,
}

package {'coffee-script':
  ensure => installed,
  provider => npm,
  require => Package['nodejs'],
}

package {'bower':
  ensure => installed,
  provider => npm,
  require => Package['nodejs'],
}
