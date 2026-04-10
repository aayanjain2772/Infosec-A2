# Generating a recipient RSA key pair
openssl genrsa -out recipient_private_key.pem 2048
openssl rsa -in recipient_private_key.pem -pubout -out recipient_public_key.pem

# Generating a random 256-bit symmetric key (binary)
openssl rand -out symmetric_key.bin 32
echo "Generated random 256-bit symmetric key (symmetric_key.bin)"

# Encrypting the symmetric key using the recipient's RSA public key
openssl rsautl -encrypt -inkey recipient_public_key.pem -pubin \
  -in symmetric_key.bin -out encrypted_symmetric_key.bin
echo "Symmetric key encrypted with recipient's public key."

# Recipient decrypts the symmetric key using their RSA private key
openssl rsautl -decrypt -inkey recipient_private_key.pem \
  -in encrypted_symmetric_key.bin -out decrypted_symmetric_key.bin
echo "Recipient decrypted the symmetric key successfully."

# Encrypting the message using the shared symmetric key 
echo "This is a confidential message protected by the shared key." > message.txt
openssl enc -aes-256-cbc -kfile symmetric_key.bin \
  -in message.txt -out encrypted_message.bin -pbkdf2
echo "Message encrypted using symmetric key."

# Decrypting the message using the decrypted symmetric key
openssl enc -d -aes-256-cbc -kfile decrypted_symmetric_key.bin \
  -in encrypted_message.bin -out decrypted_message.txt -pbkdf2
echo "Decrypted message:"
cat decrypted_message.txt
