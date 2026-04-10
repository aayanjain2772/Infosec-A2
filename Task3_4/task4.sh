#!/bin/bash
# Generate a new key pair for a user (Alice)
openssl genrsa -out alice_private_key.pem 2048
openssl rsa -in alice_private_key.pem -pubout -out alice_public_key.pem

# Create a CSR for Alice
openssl req -new -key alice_private_key.pem -out alice_csr.pem \
  -subj "/C=US/ST=State/L=City/O=AliceOrg/CN=alice@example.com"

# CA signs Alice's CSR
openssl x509 -req -in alice_csr.pem -CA ca_certificate.pem \
  -CAkey ca_private_key.pem -CAcreateserial \
  -out alice_certificate.pem -days 365

# Validate Alice's signed certificate
openssl verify -CAfile ca_certificate.pem alice_certificate.pem

# View certificate
openssl x509 -in alice_certificate.pem -text -noout
