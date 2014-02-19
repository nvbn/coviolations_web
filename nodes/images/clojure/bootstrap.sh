#!/bin/bash

puppet module install puppetlabs/apt
puppet module install puppetlabs/nodejs
puppet apply manifest.pp
