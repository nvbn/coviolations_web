user { "covio":
  ensure => present
}

sudo::sudoers { 'worlddomination':
  ensure   => 'present',
  users    => ['covio'],
  runas    => ['root'],
  cmnds    => ['ALL'],
  tags     => ['NOPASSWD'],
}

package { "build-essential":
  ensure => "installed"
}

package { "git":
  ensure => "installed"
}

package { "libyaml-dev":
  ensure => "installed"
}
