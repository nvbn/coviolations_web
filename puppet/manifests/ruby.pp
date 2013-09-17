package {'rubygems':
  ensure => installed,
}

package {'sass':
  ensure => installed,
  provider => gem,
  require => Package['rubygems'],
}
