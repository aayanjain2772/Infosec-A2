
# needham_schroeder.py
# Needham-Schroeder Shared-Key Protocol simulation and Denning-Sacco attack
# Only uses Python standard library - no external packages needed

import random
import hashlib

# ─── Simple symmetric cipher using XOR + shared key (textbook demo) ──────────

def simple_encrypt(plaintext: str, key: str) -> str:
    """XOR-based encryption using a key, output as hex string."""
    key_bytes = key.encode()
    result = []
    for i, ch in enumerate(plaintext.encode()):
        result.append(ch ^ key_bytes[i % len(key_bytes)])
    return bytes(result).hex()

def simple_decrypt(hex_ciphertext: str, key: str) -> str:
    """Reverse the XOR-based encryption."""
    key_bytes = key.encode()
    raw = bytes.fromhex(hex_ciphertext)
    result = []
    for i, byte in enumerate(raw):
        result.append(byte ^ key_bytes[i % len(key_bytes)])
    return bytes(result).decode()

def generate_nonce() -> int:
    return random.randint(10000, 99999)

def generate_session_key() -> str:
    rand = random.randint(1000, 9999)
    return f"SESSION_KEY_{rand}"


# ─── Shared long-term keys between KDC and each party ────────────────────────
KEY_ALICE_KDC = "ALICE_MASTER_SECRET"
KEY_BOB_KDC   = "BOB_MASTER_SECRET"


# ─── Normal Protocol Run ──────────────────────────────────────────────────────
print("=== Needham-Schroeder Normal Execution ===")

# Step 1: Alice sends request to KDC
nonce_a = generate_nonce()
print(f"[KDC] Received request from Alice to establish session with Bob. Nonce: {nonce_a}")

# Step 2: KDC generates session key and creates tickets
session_key = generate_session_key()
print(f"[KDC] Distributing session key '{session_key}' and secure ticket.")

# KDC sends to Alice: {session_key, nonce_a, ticket_for_bob} encrypted with Alice's master key
# ticket_for_bob = {session_key, "Alice"} encrypted with Bob's master key
ticket_for_bob   = simple_encrypt(f"{session_key}|Alice", KEY_BOB_KDC)
kdc_to_alice     = simple_encrypt(f"{session_key}|{nonce_a}|{ticket_for_bob}", KEY_ALICE_KDC)

# Step 3: Alice decrypts KDC response
alice_decrypted  = simple_decrypt(kdc_to_alice, KEY_ALICE_KDC)
parts            = alice_decrypted.split("|", 2)
alice_session    = parts[0]
alice_nonce      = parts[1]
alice_ticket     = parts[2]

# Verify nonce matches
assert alice_nonce == str(nonce_a), "Nonce mismatch - possible replay!"
print(f"[Alice] Verified KDC response. Extracted Session Key: {alice_session}")
print("[Alice] Forwarding ticket to Bob...")

# Step 4: Bob decrypts the ticket using his master key
bob_ticket_plain = simple_decrypt(alice_ticket, KEY_BOB_KDC)
bob_parts        = bob_ticket_plain.split("|")
bob_session      = bob_parts[0]
bob_identity     = bob_parts[1]

print(f"[Bob] Validated ticket for {bob_identity}. Extracted Session Key: {bob_session}")

# Step 5: Bob sends a nonce challenge to Alice (encrypted with session key)
nonce_b = generate_nonce()
print("[Bob] Sending numeric challenge to Alice...")
challenge = simple_encrypt(str(nonce_b), bob_session)

# Step 6: Alice responds with nonce_b - 1 to prove she holds the session key
c_plain   = simple_decrypt(challenge, alice_session)
response  = simple_encrypt(str(int(c_plain) - 1), alice_session)
print(f"[Alice] Responding to challenge ({c_plain} - 1)...")

# Step 7: Bob verifies Alice's response
r_plain = simple_decrypt(response, bob_session)
assert int(r_plain) == nonce_b - 1, "Authentication failed!"
print("[Bob] Mutual authentication successfully established!")


# ─── Denning-Sacco Attack ─────────────────────────────────────────────────────
print("\n\n--- Time passes. The session key expires but Mallory steals it along with the ticket ---\n")

# Mallory has obtained (by eavesdropping or disk theft) the old session_key
# and the ticket that was forwarded from Alice to Bob.
compromised_session_key = session_key
compromised_ticket      = alice_ticket

print("=== Denning-Sacco Attack Execution ===")
print("Mallory has compromised an old session key and its corresponding valid ticket to Bob.")
print("[Mallory] Replaying intercepted ticket to Bob...")

# Mallory replays the old ticket to Bob - Bob has no way to detect it is stale
mallory_ticket_plain = simple_decrypt(compromised_ticket, KEY_BOB_KDC)
mallory_parts        = mallory_ticket_plain.split("|")
mallory_session      = mallory_parts[0]
mallory_identity     = mallory_parts[1]

print(f"[Bob] Successfully decrypted the ticket. Extracted Session Key: {mallory_session} from {mallory_identity}")
print("[Bob] (Bob has no timestamp to check if this ticket is old or recently generated!)")

# Bob issues a fresh challenge, Mallory can answer it using the stolen session key
nonce_attack = generate_nonce()
print("[Bob] Sending numeric challenge to Alice (intercepted by Mallory)...")
challenge_attack = simple_encrypt(str(nonce_attack), mallory_session)

# Mallory answers because she has the session key
print(f"[Mallory] Validly responding to challenge ({nonce_attack} - 1)...")
mallory_response = simple_encrypt(str(nonce_attack - 1), compromised_session_key)

# Bob verifies - it passes because Mallory used the correct session key
verify = simple_decrypt(mallory_response, bob_session)
assert int(verify) == nonce_attack - 1
print("[Bob] Authentication successful. Bob now incorrectly trusts Mallory as Alice!")


# ─── Explanation & Mitigation ─────────────────────────────────────────────────
print("\n=== Explanation & Mitigation ===")
print("The Needham-Schroeder Shared-Key Protocol does not include a timestamp inside the ticket.")
print("Consequently, if a session key is compromised years later, an attacker like Mallory can replay")
print("the legacy ticket back to Bob. Since it authentically decodes using his master key, Bob will")
print("mistakenly trust it. The Denning-Sacco protocol mitigates this by mandating timestamps within")
print("the ticket, empowering Bob to instantly discard replays that fall outside a viable time window.")
