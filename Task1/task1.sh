# Generate a 2048-bit RSA private key
openssl genrsa -out private_key.pem 2048

#  Extract the corresponding public key
openssl rsa -in private_key.pem -pubout -out public_key.pem

# Create the message to encrypt
echo "Hello, this is a secret message." > message.txt

#  Encrypt the message using the public key (RSA PKCS#1 v1.5)
openssl rsautl -encrypt -inkey public_key.pem -pubin \
  -in message.txt -out encrypted_message.bin

# Decrypt the message using the private key
openssl rsautl -decrypt -inkey private_key.pem \
  -in encrypted_message.bin -out decrypted_message.txt

# Verify decryption
echo "Decrypted message:"
cat decrypted_message.txt
