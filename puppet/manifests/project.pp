class covio_project {
  $path = "/var/www/env/coviolations/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

  file { 'local settings':
    path => "/var/www/coviolations/coviolations_web/local.py",
    ensure => file,
    content => template("/var/www/coviolations/puppet/templates/local.py.erb"),
  }

  package {'git-core':
    ensure => latest,
  }

  exec {"install assets":
    command => 'fab install_assets',
    path => $path,
    user => 'www-data',
    require => [
      File['local settings'],
      Package['git-core']
    ],
    cwd => '/var/www/coviolations/',
  }

  exec {"compile assets":
    command => 'fab compile_assets',
    path => $path,
    user => 'www-data',
    require => File['local settings'],
    cwd => '/var/www/coviolations/',
  }

  exec {"update db":
    command => 'fab update_db',
    path => $path,
    user => 'www-data',
    require => File['local settings'],
    cwd => '/var/www/coviolations/',
  }

  exec {"collect static":
    command => 'fab collect_static',
    path => $path,
    user => 'www-data',
    require => [
      Exec['compile assets'],
      Exec['install assets']
    ],
    cwd => '/var/www/coviolations/',
  }
}
