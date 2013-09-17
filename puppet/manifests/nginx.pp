apt::ppa {'ppa:chris-lea/nginx-devel':
  notify => Package['nginx'],
}

package {'nginx':
  ensure => latest,
}

service { 'nginx':
  ensure => running,
  enable => true,
  require => Package['nginx']
}

file { '/etc/nginx/sites-enabled/default':
  ensure => absent,
  require => Package['nginx']
}

file { 'sites-available config':
  path => "/etc/nginx/sites-available/${domain}.conf",
  ensure => file,
  content => template("/var/www/coviolations/puppet/templates/nginx.erb"),
  require => Package['nginx']
}

file { "/etc/nginx/sites-enabled/${domain}.conf":
  ensure => link,
  target => "/etc/nginx/sites-available/${domain}.conf",
  require => File['sites-available config'],
  notify => Service['nginx']
}
