# 1. Generating a CA private key and self-signed certificate
openssl genpkey -algorithm RSA -out ca_private_key.pem -pkeyopt rsa_keygen_bits:2048
openssl req -x509 -new -nodes -key ca_private_key.pem -sha256 -days 365 -out ca_certificate.pem -subj "/C=US/ST=State/L=City/O=MyCA/CN=My Root CA"

# 2. Generating a Client private key and the Certificate Signing Request 
openssl genpkey -algorithm RSA -out client_private_key.pem -pkeyopt rsa_keygen_bits:2048
openssl req -new -key client_private_key.pem -out client_csr.pem -subj "/C=US/ST=State/L=City/O=ClientOrg/CN=Client Public Key"

# Extracting the client public key 
openssl rsa -pubout -in client_private_key.pem -out client_public_key.pem

# 3. Using the CA to sign the CSR, issuing a certificate
openssl x509 -req -in client_csr.pem -CA ca_certificate.pem -CAkey ca_private_key.pem -CAcreateserial -out client_certificate.pem -days 365 -sha256

# 4. Verifying the certificate using the CA's certificate
openssl verify -CAfile ca_certificate.pem client_certificate.pem
