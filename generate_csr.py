#!/usr/bin/env python
# encoding: utf-8
# Tested with Pythons 2.7 and 3.4

# Licensed under the BSD 2-Clause License <https://opensource.org/licenses/BSD-2-Clause>
# Authors:
# - Robert Buchholz rbu goodpoint de
# - Martin Häcker mhaecker ät mac dot com


import argparse
import codecs
import os
import sys
from subprocess import check_call
from tempfile import NamedTemporaryFile
PY3 = sys.version_info[0] == 3

# SSL certificate defaults.
# Fill in if you copy this script or export as environment variables.
DEFAULTS = dict(
    REQ_COUNTRY='XX',
    REQ_PROVINCE='',
    REQ_CITY='',
    REQ_ORG='',
    REQ_OU='',
    REQ_EMAIL='',
)

def parse_args():
    parser = argparse.ArgumentParser(
        description='Generate SSL CSRs with Subject Alternative Names')
    parser.add_argument('--batch', dest='batch', action='store_true',
        default=False, help='Batch mode, supress interaction and go with defaults.')
    parser.add_argument('--key', dest='key', metavar='PRIVATE_KEY_FILE',
        help="""Path to a private key file to generate a CSR for.
            To generate a key, consider calling 'openssl genrsa -out private.key 4096'
        """)
    parser.add_argument('domains', metavar='DOMAIN', nargs='+',
        help='Domain names to request. First domain is the common name.')
    return parser.parse_args()

def environment():
    env = DEFAULTS.copy()
    env.update(os.environ)
    return env

def ensure_text(maybe_text):
    text_type = str if PY3 else unicode
    if isinstance(maybe_text, text_type):
        return maybe_text
    return maybe_text.decode('utf-8')

def write_openssl_config_to(fd, domains):
    fd.write(OPEN_SSL_CONF)
    fd.write(u'commonName_default=%s\n\n' % ensure_text(domains[0]))
    fd.write(u'[SAN]\n')
    fd.write(u'subjectAltName=')
    fd.write(u','.join(map(lambda domain: u'DNS:%s' % ensure_text(domain), domains)))
    fd.write(u'\n')
    fd.flush()

def main():
    arguments = parse_args()
    with NamedTemporaryFile() as config_fd:
        config_fd = codecs.getwriter('utf-8')(config_fd)
        write_openssl_config_to(config_fd, arguments.domains)
        batch_params = ['-batch'] if arguments.batch else []
        
        check_call(
            [
                'openssl',
                'req', '-new', '-sha256',
                '-key', arguments.key,
                '-reqexts', 'SAN',
                '-config', config_fd.name,
            ] + batch_params,
            env=environment(),
        )

OPEN_SSL_CONF = u"""
HOME			= .
RANDFILE		= $ENV::HOME/.rnd

[ req ]
default_bits		= 2048
default_md		= sha256
default_keyfile 	= privkey.pem
distinguished_name	= req_distinguished_name
x509_extensions	= v3_ca	# The extentions to add to the self signed cert
string_mask = utf8only

[ v3_ca ]
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid:always,issuer
basicConstraints = CA:true

[ req_distinguished_name ]
countryName			= Country Name (2 letter code)
countryName_default		= $ENV::REQ_COUNTRY
countryName_min			= 2
countryName_max			= 2

stateOrProvinceName		= State or Province Name (full name)
stateOrProvinceName_default	= $ENV::REQ_PROVINCE

localityName			= Locality Name (eg, city)
localityName_default		= $ENV::REQ_CITY

0.organizationName		= Organization Name (eg, company)
0.organizationName_default	= $ENV::REQ_ORG

organizationalUnitName		= Organizational Unit Name (eg, section)
organizationalUnitName_default	= $ENV::REQ_OU

commonName			= Common Name (eg, your name or your server\'s hostname)
commonName_max			= 64

emailAddress			= Email Address
emailAddress_max		= 64
emailAddress_default		= $ENV::REQ_EMAIL
"""

if __name__ == '__main__':
    main()
