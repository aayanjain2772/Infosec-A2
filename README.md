# Information Security Assignment 2

This repository contains the deliverables for Assignment 2 of CS-3610. The assignment tasks include generating key pairs, symmetric key exchanges, certificate authority setup, signature verification, Man-in-the-Middle (MITM) attacks, and analyzing the Denning-Sacco attack on the Needham-Schroeder protocol.

## Task 1: Generating Public and Private Keys

**Description:**
Using OpenSSL, a 2048-bit RSA key pair is generated to demonstrate asymmetric encryption.

**Commands Used:**
```bash
# 1. Generate a 2048-bit RSA private key
openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:2048

# 2. Extract the corresponding public key
openssl rsa -pubout -in private_key.pem -out public_key.pem

# 3. Encrypt a message with the public key
echo "This is a secret message to test asymmetric encryption." > message.txt
openssl pkeyutl -encrypt -pubin -inkey public_key.pem -in message.txt -out encrypted_message.bin

# 4. Decrypt the message with the private key
openssl pkeyutl -decrypt -inkey private_key.pem -in encrypted_message.bin -out decrypted_message.txt
```

**Brief Explanation:**
Asymmetric encryption ensures confidentiality by utilizing a mathematically linked pair of keys—a public key and a private key. The public key is shared openly and is used to encrypt messages. Because of the trapdoor functionality of underlying mathematical problem (like integer factorization in RSA), the only way to reverse the encryption is by using the corresponding private key, ensuring that only the rightful owner (the entity holding the private key) can read it.

---

## Task 2: Secure Symmetric Key Exchange

**Description:**
To efficiently encrypt large amounts of data, symmetric encryption is used. To share the symmetric key securely, we use asymmetric encryption.

**Commands Used:**
```bash
# Setup: Generate recipient's key pair 
openssl genpkey -algorithm RSA -out recipient_private_key.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in recipient_private_key.pem -out recipient_public_key.pem

# 1. Generate a random 256-bit symmetric AES key (32 bytes)
openssl rand -out symmetric_key.bin 32

# 2. Encrypt the symmetric key using the recipient’s public key
openssl pkeyutl -encrypt -pubin -inkey recipient_public_key.pem -in symmetric_key.bin -out encrypted_symmetric_key.bin

# 3. The recipient decrypts it using their private key
openssl pkeyutl -decrypt -inkey recipient_private_key.pem -in encrypted_symmetric_key.bin -out decrypted_symmetric_key.bin

# 4. Use the shared key to encrypt a message
echo "This is confidential data encrypted with the symmetric key." > message.txt
openssl enc -aes-256-cbc -salt -in message.txt -out encrypted_message.bin -pass file:decrypted_symmetric_key.bin -pbkdf2

# 5. Decrypt the message
openssl enc -d -aes-256-cbc -in encrypted_message.bin -out decrypted_message.txt -pass file:decrypted_symmetric_key.bin -pbkdf2
```

**Security Measures:**
The main mechanism here forms the basis of hybrid cryptosystems. Symmetric keys are fast but hard to exchange securely. Asymmetric cryptography is computationally expensive but enables secure exchange. By encapsulating the symmetric key inside an asymmetric cipher (using the recipient's public key), we provide confidentiality over an insecure channel. Only the recipient with the private key can extract the symmetric key.

---

## Task 3 & 4: Setting Up a Certificate Authority and Signing a Key

**Description:**
A Certificate Authority (CA) acts as a trusted third party. Generating a self-signed root CA certificate, generating a client Certificate Signing Request (CSR), and signing it natively establishes trust.

**Commands Used:**
```bash
# TASK 3: Setting Up a Certificate Authority
# 1. Generate a CA private key and a self-signed certificate
openssl genpkey -algorithm RSA -out ca_private_key.pem -pkeyopt rsa_keygen_bits:2048
openssl req -x509 -new -nodes -key ca_private_key.pem -sha256 -days 365 -out ca_certificate.pem -subj "/C=US/ST=State/L=City/O=MyCA/CN=My Root CA"

# TASK 3 & 4: Create a CSR, Public Key, and Sign with CA
# 2. Generate a Client private key and a CSR
openssl genpkey -algorithm RSA -out client_private_key.pem -pkeyopt rsa_keygen_bits:2048
openssl req -new -key client_private_key.pem -out client_csr.pem -subj "/C=US/ST=State/L=City/O=ClientOrg/CN=Client Public Key"

# Extract the client public key
openssl rsa -pubout -in client_private_key.pem -out client_public_key.pem

# 3. CA signs the CSR, creating a legitimate certificate
openssl x509 -req -in client_csr.pem -CA ca_certificate.pem -CAkey ca_private_key.pem -CAcreateserial -out client_certificate.pem -days 365 -sha256

# 4. Verify the certificate using the CA's certificate
openssl verify -CAfile ca_certificate.pem client_certificate.pem
```
*Output of Verification:*
`client_certificate.pem: OK`

**Explanation of CA and Digital Certificates:**
The CA plays a pivotal role in PKI (Public Key Infrastructure). When communicating over networks, entities need reassurance that the public key actually belongs to the person claiming it. A CA digitally signs the entity's public key (along with metadata like organization identity), producing a "Digital Certificate". Anyone possessing the CA's globally trusted public key can verify the certificate's signature, confirming the client's identity without requiring out-of-band communications. 

---

## Task 5: Man-in-the-Middle (MITM) Attack

**Description:**
A MITM attack conceptually allows an adversary (Mallory) to secretly intercept and relay messages. In unauthenticated key exchanges like early Diffie-Hellman, the parties agree on a secret but don't verify WHO they are agreeing with.

A python script (`Task5/mitm_attack.py`) simulates this attack. Mallory intercepts Alice's public values, injects her own towards Bob, and does the same backward. As a result, Mallory shares one session key with Alice, and another with Bob.

**Python Execution Output (`Task5/output.txt`):**
```text
=== Normal Diffie-Hellman Key Exchange ===
Alice's public key: 8
Bob's public key: 19
[Alice] computed shared secret: 2
[Bob] computed shared secret: 2
Alice and Bob have successfully established a shared secret.

=== Man-in-the-Middle (MITM) Attack by Mallory ===
Mallory intercepts keys from Alice and Bob...
Mallory passes her public key 9 to Alice instead of Bob's.
Mallory passes her public key 22 to Bob instead of Alice's.

[Alice] computed shared secret: 3
[Mallory_A] computed shared secret: 3
[Bob] computed shared secret: 13
[Mallory_B] computed shared secret: 13

=== MITM Attack Results ===
Mallory successfully established two separate shared secrets!
Secret with Alice: 3 (Alice thinks this is shared with Bob)
Secret with Bob: 13 (Bob thinks this is shared with Alice)
Mallory can now intercept messages from Alice, decrypt them, read/modify them, and re-encrypt them for Bob.
```

**Countermeasures:**
To thwart MITM, unauthenticated exchanges should not be used. Authenticated key exchange (using signatures) acts as a remedy. Parties can sign their DH parameters using a private key backed by a Digital Certificate (PKI infrastructure, as covered in Task 3 and 4). Protocols such as TLS implement these measures explicitly.

---

## Task 6: Needham-Schroeder Protocol and Denning-Sacco Attack

**Description:**
The Needham-Schroeder symmetric key protocol was a landmark mechanism for key distribution via a trusted Key Distribution Center (KDC). However, it possessed a fatal flaw discovered by Denning and Sacco: lack of timestamps on the ticket. 

The Python script (`Task6/needham_schroeder.py`) implements the interaction between Alice, Bob, and the KDC. Following the protocol execution, the script demonstrates the Denning-Sacco attack, where Mallory accesses a stale, previously used session key and corresponding ticket, successfully authenticating herself to Bob as Alice. 

**Python Execution Output (`Task6/output.txt`):**
```text
=== Needham-Schroeder Normal Protocol Execution ===
[KDC] Received request from Alice to communicate with Bob (Nonce: N1)
[KDC] Sending session key and ticket to Alice
[Alice] Decrypted KDC response, verified N1: N1 == N1
[Alice] Sending ticket to Bob...
[Bob] Decrypted ticket. Session key: K_AB_SESSION from Alice
[Bob] Sending challenge ENC_KAB(N2) to Alice
[Alice] Sending response ENC_KAB(N2-1) back to Bob
[Bob] Verified response. Mutual authentication successful.

--- Time passes. The session key 'K_AB_SESSION' is now stale and was found by Mallory ---

=== Denning-Sacco Attack Execution ===
Mallory has compromised an old session key and its corresponding ticket to Bob.
[Mallory] Replaying old ticket to Bob: ENC_KB({"session_key": "K_AB_SESSION", "initiator": "Alice"})
[Bob] Decrypted ticket. Session key: K_AB_SESSION from Alice
[Bob] Sending challenge ENC_KAB(N_BOB_NEW) to Alice (intercepted by Mallory)
[Mallory] Sending valid response ENC_KAB(N_BOB_NEW-1) using the compromised session key
[Bob] Verified response. Bob incorrectly believes he is securely communicating with Alice!

=== Mitigation ===
The Denning-Sacco attack is possible because the Needham-Schroeder protocol does not use timestamps.
Without timestamps, Bob has no way of knowing if the ticket is fresh or an old replay.
Mitigation: Include timestamps in tickets (like in Kerberos) so participants can reject old tickets.
```

**Explanation & Mitigation Techniques:**
The attack happens because the KDC issues an encrypted ticket specifying that a specific key belongs to Alice. Because the ticket doesn't include an expiration time or a timestamp, Bob inherently believes any ticket decrypted successfully using his master key is fresh and authentic. If Mallory brute forces a very old session key, she can keep replying the old ticket to Bob natively, and answer any challenges because she knows the key.
**Mitigation:** By supplementing the Kerberos specification and the Denning-Sacco resolution logic, the ticket distributed by the KDC must possess a Time-To-Live (TTL) or Timestamp. If an adversary attempts to replay it outside the designated window, Bob can simply reject the connection request.
