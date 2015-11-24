#!/usr/bin/env bash

DOMAIN=$1

if [ -z "$DOMAIN" ]; then
  echo -n 'Enter root domain (no www): '
  read input_d
  DOMAIN=$input_d
fi

[ -d certs ] || mkdir certs

# Easiest to generate conf file for each
# certificate creation process
OpenSSLConf="$DOMAIN"-openssl.cnf

cat >"$OpenSSLConf" <<EOL
[req]
req_extensions = v3_req
distinguished_name = req_distinguished_name

[ req_distinguished_name ]
countryName                 = Country
countryName_default         = US
stateOrProvinceName         = State
stateOrProvinceName_default = CA
localityName                = City
localityName_default        = Santa Clara
commonName                  = Common Name
commonName_default          = *.$DOMAIN

[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DOMAIN
DNS.2 = *.$DOMAIN
EOL

# Create Private RSA Key
openssl genrsa -out "certs/$DOMAIN".key 1024

# Create Certifcate Signing Request
openssl req -batch -new -key "certs/$DOMAIN".key -out "certs/$DOMAIN".csr -config "$OpenSSLConf"

# Create Certifcate
openssl x509 -req -days 365 -in "certs/$DOMAIN".csr \
-signkey "certs/$DOMAIN".key -out "certs/$DOMAIN".crt \
-extensions v3_req \
-extfile "$OpenSSLConf"

# Nix the configfile
rm -- "$OpenSSLConf"
