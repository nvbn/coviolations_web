file { 'local settings':
  path => "/var/www/coviolations/coviolations_web/local.py",
  ensure => file,
  content => template("/var/www/coviolations/puppet/templates/local.py.erb"),
}
