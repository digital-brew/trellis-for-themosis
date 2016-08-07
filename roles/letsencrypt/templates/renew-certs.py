#!/usr/bin/env python

import hashlib
import os
import sys
import time

from subprocess import CalledProcessError, check_output, STDOUT

certs_dir = '{{ letsencrypt_certs_dir }}'
failed = False
sites = {{ wordpress_sites }}
sites = dict((k, v) for k, v in sites.iteritems() if 'ssl' in v and v['ssl'].get('enabled', False) and v['ssl'].get('provider', 'manual') == 'letsencrypt')

for name, site in sites.iteritems():
    canonical_hosts = list(hosts['canonical'] for hosts in site['site_hosts'])
    redirect_hosts = sum((hosts.get('redirects') for hosts in site['site_hosts'] if hosts.get('redirects', None)), [])
    site_hosts = list(set(canonical_hosts) | set(redirect_hosts))
    hosts = ''.join(site_hosts)
    hosts_hash = hashlib.md5(hosts).hexdigest()

    cert_path = os.path.join(certs_dir, name + '-' + hosts_hash + '.cert')
    bundled_cert_path = os.path.join(certs_dir, name + '-' + hosts_hash + '-bundled.cert')

    if os.access(cert_path, os.F_OK):
        stat = os.stat(cert_path)
        print 'Certificate file ' + cert_path + ' already exists'

        if time.time() - stat.st_mtime < {{ letsencrypt_min_renewal_age }} * 86400:
            print '  The certificate is younger than {{ letsencrypt_min_renewal_age }} days. Not creating a new certificate.\n'
            continue

    print 'Generating certificate for ' + name

    cmd = ('/usr/bin/env python {{ acme_tiny_software_directory }}/acme_tiny.py '
           '--ca {{ letsencrypt_ca }} '
           '--account-key {{ letsencrypt_account_key }} '
           '--csr {{ acme_tiny_data_directory }}/csrs/{0}-{1}.csr '
           '--acme-dir {{ acme_tiny_challenges_directory }}'
           ).format(name, hosts_hash)

    try:
        cert = check_output(cmd, stderr=STDOUT, shell=True)
    except CalledProcessError as e:
        failed = True
        print 'Error while generating certificate for ' + name
        print e.output
    else:
        with open(cert_path, 'w') as cert_file:
            cert_file.write(cert)

        with open('{{ letsencrypt_intermediate_cert_path }}') as intermediate_cert_file:
            intermediate_cert = intermediate_cert_file.read()

        with open(bundled_cert_path, 'w') as bundled_file:
            bundled_file.write(''.join([cert, intermediate_cert]))

        print 'Created certificate for ' + name

if failed:
    sys.exit(1)
