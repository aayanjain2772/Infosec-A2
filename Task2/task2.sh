#!/bin/bash
# Generate recipient's key pair for key exchange
openssl genpkey -algorithm RSA -out recipient_private_key.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in recipient_private_key.pem -out recipient_public_key.pem
# 1. Generate a random symmetric key (256-bit AES key)
openssl rand -out symmetric_key.bin 32
# 2. Encrypt the symmetric key using the recipient’s public key
openssl pkeyutl -encrypt -pubin -inkey recipient_public_key.pem -in symmetric_key.bin -out encrypted_symmetric_key.bin
# 3. The recipient decrypts it using their private key
openssl pkeyutl -decrypt -inkey recipient_private_key.pem -in encrypted_symmetric_key.bin -out decrypted_symmetric_key.bin
# 4. Use the shared key to encrypt and decrypt a message
echo "This is confidential data encrypted with the exchanged symmetric key." > message.txt
openssl enc -aes-256-cbc -salt -in message.txt -out encrypted_message.bin -pass file:decrypted_symmetric_key.bin -pbkdf2
openssl enc -d -aes-256-cbc -in encrypted_message.bin -out decrypted_message.txt -pass file:decrypted_symmetric_key.bin -pbkdf2
