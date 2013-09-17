class covio_project {
  file { 'local settings':
    path => "/var/www/coviolations/coviolations_web/local.py",
    ensure => file,
    content => template("/var/www/coviolations/puppet/templates/local.py.erb"),
  }

  exec {"install":
    command => 'fab install:production',
    require => File['local settings'],
  }
}
