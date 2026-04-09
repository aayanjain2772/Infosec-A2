#!/bin/bash
# Generate a 2048-bit RSA private key
openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:2048
# Extract the corresponding public key
openssl rsa -pubout -in private_key.pem -out public_key.pem
# Create a sample message
echo "This is a secret message to test asymmetric encryption." > message.txt
# Encrypt the message with the public key
openssl pkeyutl -encrypt -pubin -inkey public_key.pem -in message.txt -out encrypted_message.bin
# Decrypt the message with the private key
openssl pkeyutl -decrypt -inkey private_key.pem -in encrypted_message.bin -out decrypted_message.txt
