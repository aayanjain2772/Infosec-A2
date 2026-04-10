#!/bin/bash
# Task 1: Generating Public and Private Keys using OpenSSL

# Step 1: Generate a 2048-bit RSA private key
openssl genrsa -out private_key.pem 2048

# Step 2: Extract the corresponding public key
openssl rsa -in private_key.pem -pubout -out public_key.pem

# Step 3a: Create the message to encrypt
echo "Hello, this is a secret message." > message.txt

# Step 3b: Encrypt the message using the public key (RSA PKCS#1 v1.5)
openssl rsautl -encrypt -inkey public_key.pem -pubin \
  -in message.txt -out encrypted_message.bin

# Step 3c: Decrypt the message using the private key
openssl rsautl -decrypt -inkey private_key.pem \
  -in encrypted_message.bin -out decrypted_message.txt

# Step 4: Verify decryption
echo "Decrypted message:"
cat decrypted_message.txt
