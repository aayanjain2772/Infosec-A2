# Generating CA private key and self-signed certificate
openssl genrsa -out ca_private_key.pem 2048
openssl req -new -x509 -key ca_private_key.pem -out ca_certificate.pem -days 365 \
  -subj "/C=US/ST=State/L=City/O=MyCA/CN=MyRootCA"

# Generating a new key pair and CSR (for "server/user")
openssl genrsa -out server_private_key.pem 2048
openssl req -new -key server_private_key.pem -out server_csr.pem \
  -subj "/C=US/ST=State/L=City/O=MyOrg/CN=myserver.example.com"

# CA signs the CSR
openssl x509 -req -in server_csr.pem -CA ca_certificate.pem \
  -CAkey ca_private_key.pem -CAcreateserial \
  -out server_certificate.pem -days 365

#Verifying the certificate against the CA
openssl verify -CAfile ca_certificate.pem server_certificate.pem

# Viewing certificate details
openssl x509 -in server_certificate.pem -text -noout
