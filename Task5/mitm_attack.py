# mitm_attack.py
# Man-in-the-Middle attack simulation using Diffie-Hellman key exchange

import random

# Small DH parameters 
# In real world these would be much larger
p = 23   # prime modulus
g = 5    # generator

def dh_private_key():
    return random.randint(2, p - 2)

def dh_public_key(private):
    return pow(g, private, p)

def dh_shared_secret(their_public, my_private):
    return pow(their_public, my_private, p)


print("=== Normal Diffie-Hellman Key Exchange ===")

alice_private = dh_private_key()
bob_private   = dh_private_key()

alice_public = dh_public_key(alice_private)
bob_public   = dh_public_key(bob_private)

print(f"Alice's public key: {alice_public}")
print(f"Bob's public key: {bob_public}")

alice_secret = dh_shared_secret(bob_public, alice_private)
bob_secret   = dh_shared_secret(alice_public, bob_private)

print(f"[Alice] computed shared secret: {alice_secret}")
print(f"[Bob] computed shared secret: {bob_secret}")

if alice_secret == bob_secret:
    print("Alice and Bob have successfully established a shared secret.")


print("\n=== Man-in-the-Middle (MITM) Attack by Mallory ===")

mallory_private_a = dh_private_key()   # Mallory's key for talk with Alice
mallory_private_b = dh_private_key()   # Mallory's key for talk with Bob

mallory_public_a = dh_public_key(mallory_private_a)
mallory_public_b = dh_public_key(mallory_private_b)

print("Mallory intercepts keys from Alice and Bob...")
print(f"Mallory passes her public key {mallory_public_a} to Alice instead of Bob's.")
print(f"Mallory passes her public key {mallory_public_b} to Bob instead of Alice's.")

# Alice thinks she is computing secret with Bob but actually with Mallory
alice_secret_mitm    = dh_shared_secret(mallory_public_a, alice_private)
mallory_secret_alice = dh_shared_secret(alice_public, mallory_private_a)

# Bob thinks he is computing secret with Alice but actually with Mallory
bob_secret_mitm      = dh_shared_secret(mallory_public_b, bob_private)
mallory_secret_bob   = dh_shared_secret(bob_public, mallory_private_b)

print(f"\n[Alice] computed shared secret: {alice_secret_mitm}")
print(f"[Mallory_A] computed shared secret: {mallory_secret_alice}")
print(f"[Bob] computed shared secret: {bob_secret_mitm}")
print(f"[Mallory_B] computed shared secret: {mallory_secret_bob}")

print("\n=== MITM Attack Results ===")
print("Mallory successfully established two separate shared secrets!")
print(f"Secret with Alice: {alice_secret_mitm} (Alice thinks this is shared with Bob)")
print(f"Secret with Bob: {bob_secret_mitm} (Bob thinks this is shared with Alice)")
print("Mallory can now intercept messages from Alice, decrypt them, read/modify them, and re-encrypt them for Bob.")
