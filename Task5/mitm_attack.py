# Diffie-Hellman Key Exchange Man-in-the-Middle (MITM) Attack Demonstration

# Shared parameters (typically large primes, testing with smaller values)
p = 23  # Prime modulus
g = 5   # Generator

class Entity:
    def __init__(self, name, private_key):
        self.name = name
        self.private_key = private_key
        self.public_key = (g ** private_key) % p
        self.shared_secret = None

    def compute_secret(self, other_public_key):
        self.shared_secret = (other_public_key ** self.private_key) % p
        print(f"[{self.name}] computed shared secret: {self.shared_secret}")

def main():
    print("=== Normal Diffie-Hellman Key Exchange ===")
    alice = Entity("Alice", 6)
    bob = Entity("Bob", 15)
    
    print(f"Alice's public key: {alice.public_key}")
    print(f"Bob's public key: {bob.public_key}")
    
    alice.compute_secret(bob.public_key)
    bob.compute_secret(alice.public_key)
    print("Alice and Bob have successfully established a shared secret.\n")

    print("=== Man-in-the-Middle (MITM) Attack by Mallory ===")
    alice = Entity("Alice", 6)
    bob = Entity("Bob", 15)
    
    # Mallory sets up two separate key exchanges
    mallory_to_alice = Entity("Mallory_A", 10)
    mallory_to_bob = Entity("Mallory_B", 11)

    print("Mallory intercepts keys from Alice and Bob...")
    print(f"Mallory passes her public key {mallory_to_alice.public_key} to Alice instead of Bob's.")
    print(f"Mallory passes her public key {mallory_to_bob.public_key} to Bob instead of Alice's.\n")

    # Alice thinks she is communicating with Bob, but computes secret with Mallory
    alice.compute_secret(mallory_to_alice.public_key)
    mallory_to_alice.compute_secret(alice.public_key)

    # Bob thinks he is communicating with Alice, but computes secret with Mallory
    bob.compute_secret(mallory_to_bob.public_key)
    mallory_to_bob.compute_secret(bob.public_key)

    print("\n=== MITM Attack Results ===")
    print("Mallory successfully established two separate shared secrets!")
    print(f"Secret with Alice: {mallory_to_alice.shared_secret} (Alice thinks this is shared with Bob)")
    print(f"Secret with Bob: {mallory_to_bob.shared_secret} (Bob thinks this is shared with Alice)")
    print("Mallory can now intercept messages from Alice, decrypt them, read/modify them, and re-encrypt them for Bob.")

if __name__ == "__main__":
    main()
