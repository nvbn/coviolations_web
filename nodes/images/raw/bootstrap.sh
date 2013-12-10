#!/bin/bash

wget http://apt.puppetlabs.com/puppetlabs-release-precise.deb
dpkg -i puppetlabs-release-precise.deb
apt-get -y update
apt-get -y upgrade
apt-get -y install puppet hiera
puppet module install arnoudj/sudo
puppet apply manifest.pp
