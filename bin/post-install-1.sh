#!/bin/sh

mkdir group_vars/development &&
cp -R group_vars/local/wordpress_sites.yml group_vars/development/wordpress_sites.yml &&
vagrant trellis-cert trust 
