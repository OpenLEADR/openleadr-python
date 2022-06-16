set -e

echo "Please make sure the line RANDFILE = ... is commented out in your /etc/ssl/openssl.conf."

echo "Generating the CA key"
openssl genrsa -out dummy_ca.key 4096

echo "Generating the CA cert"
openssl req -x509 -new -subj "/C=NL/ST=Other/O=OpenLEADR Dummy CA/CN=dummy-ca.openleadr.org" -nodes -key dummy_ca.key -sha256 -days 3650 -out dummy_ca.crt

echo "Generating the VTN key"
openssl genrsa -out dummy_vtn.key 2048

echo "Generating the VTN Certificate Signing Request"
openssl req -new -sha256 -key dummy_vtn.key -subj "/C=NL/ST=Other/O=OpenLEADR Dummy VTN/CN=localhost" -out dummy_vtn.csr

echo "Signing the VTN CSR, generating the VTN certificate"
openssl x509 -req -in dummy_vtn.csr -CA dummy_ca.crt -CAkey dummy_ca.key -CAcreateserial -out dummy_vtn.crt -days 3650 -sha256

echo "Generating the VEN key"
openssl genrsa -out dummy_ven.key 2048

echo "Generating the VEN Certificate Signing Request"
openssl req -new -sha256 -key dummy_ven.key -subj "/C=NL/ST=Other/O=OpenLEADR Dummy VEN/CN=dummy-ven.openleadr.org" -out dummy_ven.csr

echo "Signing the VTN CSR, generating the VEN certificate"
openssl x509 -req -in dummy_ven.csr -CA dummy_ca.crt -CAkey dummy_ca.key -CAcreateserial -out dummy_ven.crt -days 3650 -sha256
