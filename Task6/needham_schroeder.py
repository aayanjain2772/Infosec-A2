import json
import base64
import random

# A simple simulated encryption mechanism using Base64
# It prefixes the plaintext with the key to simulate a "locked" message.
# In a real environment, AES or another strong symmetric cipher would be used.
def simulate_encrypt(key, plaintext):
    combined = f"{key}::{plaintext}"
    encoded_bytes = base64.b64encode(combined.encode('utf-8'))
    return encoded_bytes.decode('utf-8')

def simulate_decrypt(key, ciphertext):
    try:
        decoded_bytes = base64.b64decode(ciphertext.encode('utf-8'))
        combined = decoded_bytes.decode('utf-8')
        if combined.startswith(f"{key}::"):
            return combined[len(f"{key}::"):]
        else:
            return None # Decryption failed / wrong key
    except Exception:
        return None

class KeyDistributionCenter:
    def __init__(self):
        # KDC shares symmetric keys with Alice and Bob
        self.keys = {"Alice": "MASTER_KEY_ALICE", "Bob": "MASTER_KEY_BOB"}

    def request_session(self, initiator, target, nonce1):
        print(f"[KDC] Received request from {initiator} to establish session with {target}. Nonce: {nonce1}")
        
        # Generate a new session key
        session_key = f"SESSION_KEY_{random.randint(1000, 9999)}"
        
        # 1. Create a ticket for the target (Bob), encrypted with Bob's master key
        ticket_payload = json.dumps({"session_key": session_key, "initiator": initiator})
        encrypted_ticket = simulate_encrypt(self.keys[target], ticket_payload)
        
        # 2. Create the response for the initiator (Alice), encrypted with Alice's master key
        response_payload = json.dumps({
            "nonce1": nonce1,
            "target": target,
            "session_key": session_key,
            "ticket_to_target": encrypted_ticket
        })
        encrypted_response = simulate_encrypt(self.keys[initiator], response_payload)
        
        print(f"[KDC] Distributing session key '{session_key}' and secure ticket.")
        return encrypted_response

class Node:
    def __init__(self, name, master_key):
        self.name = name
        self.master_key = master_key

    def send_challenge(self, session_key):
        nonce = random.randint(10000, 99999)
        challenge_msg = simulate_encrypt(session_key, str(nonce))
        return nonce, challenge_msg

def normal_protocol():
    print("=== Needham-Schroeder Normal Execution ===")
    kdc = KeyDistributionCenter()
    alice = Node("Alice", "MASTER_KEY_ALICE")
    bob = Node("Bob", "MASTER_KEY_BOB")
    
    # Step 1: Alice requests a session
    nonce1 = random.randint(10000, 99999)
    encrypted_response_from_kdc = kdc.request_session(alice.name, bob.name, nonce1)
    
    # Step 2: Alice decrypts response from KDC
    decrypted_str = simulate_decrypt(alice.master_key, encrypted_response_from_kdc)
    if not decrypted_str:
        print("[Alice] Failed to decrypt KDC response.")
        return None, None

    kdc_data = json.loads(decrypted_str)
    
    # Verification
    if kdc_data['nonce1'] != nonce1:
        print("[Alice] Nonce 1 mismatch! Potential replay attack detected.")
        return None, None
        
    session_key = kdc_data['session_key']
    ticket_to_bob = kdc_data['ticket_to_target']
    print(f"[Alice] Verified KDC response. Extracted Session Key: {session_key}")
    
    # Step 3: Alice sends the ticket to Bob
    print(f"[Alice] Forwarding ticket to Bob...")
    bob_decrypted_str = simulate_decrypt(bob.master_key, ticket_to_bob)
    if not bob_decrypted_str:
        print("[Bob] Failed to decrypt incoming ticket.")
        return None, None
        
    bob_data = json.loads(bob_decrypted_str)
    bob_session_key = bob_data['session_key']
    initiator_name = bob_data['initiator']
    print(f"[Bob] Validated ticket for {initiator_name}. Extracted Session Key: {bob_session_key}")
    
    # Step 4: Bob sends a challenge to Alice to prove she holds the session key
    nonce2, challenge_msg = bob.send_challenge(bob_session_key)
    print(f"[Bob] Sending numeric challenge to Alice...")
    
    # Step 5: Alice solves the challenge (Nonce - 1) and responds
    decrypted_challenge_str = simulate_decrypt(session_key, challenge_msg)
    received_nonce2 = int(decrypted_challenge_str)
    
    response_msg = simulate_encrypt(session_key, str(received_nonce2 - 1))
    print(f"[Alice] Responding to challenge ({received_nonce2} - 1)...")
    
    # Bob verifies the response
    decrypted_response_str = simulate_decrypt(bob_session_key, response_msg)
    if int(decrypted_response_str) == nonce2 - 1:
        print("[Bob] Mutual authentication successfully established!\n")
        return session_key, ticket_to_bob
    else:
        print("[Bob] Mutual authentication failed.")
        return None, None

def denning_sacco_attack(stale_session_key, intercepted_ticket):
    print("=== Denning-Sacco Attack Execution ===")
    print("Mallory has compromised an old session key and its corresponding valid ticket to Bob.")
    
    bob = Node("Bob", "MASTER_KEY_BOB")
    
    print(f"[Mallory] Replaying intercepted ticket to Bob...")
    bob_decrypted_str = simulate_decrypt(bob.master_key, intercepted_ticket)
    
    if bob_decrypted_str:
        bob_data = json.loads(bob_decrypted_str)
        bob_session_key = bob_data['session_key']
        print(f"[Bob] Successfully decrypted the ticket. Extracted Session Key: {bob_session_key} from {bob_data['initiator']}")
        print(f"[Bob] (Bob has no timestamp to check if this ticket is old or recently generated!)")
        
        # Bob challenges the initiator (Mallory in this case)
        nonce_bob, challenge_msg = bob.send_challenge(bob_session_key)
        print(f"[Bob] Sending numeric challenge to Alice (intercepted by Mallory)...")
        
        # Mallory responds pretending to be Alice because she owns the compromised session key
        decrypted_challenge_str = simulate_decrypt(stale_session_key, challenge_msg)
        received_nonce = int(decrypted_challenge_str)
        
        response_msg = simulate_encrypt(stale_session_key, str(received_nonce - 1))
        print(f"[Mallory] Validly responding to challenge ({received_nonce} - 1)...")
        
        # Bob validates
        decrypted_response_str = simulate_decrypt(bob_session_key, response_msg)
        if int(decrypted_response_str) == nonce_bob - 1:
            print("[Bob] Authentication successful. Bob now incorrectly trusts Mallory as Alice!")

def main():
    session_key, ticket = normal_protocol()
    
    if session_key and ticket:
        print("\n--- Time passes. The session key expires but Mallory steals it along with the ticket ---\n")
        denning_sacco_attack(session_key, ticket)
        
        print("\n=== Explanation & Mitigation ===")
        print("The Needham-Schroeder Shared-Key Protocol does not include a timestamp inside the ticket.")
        print("Consequently, if a session key is compromised years later, an attacker like Mallory can replay")
        print("the legacy ticket back to Bob. Since it authentically decodes using his master key, Bob will")
        print("mistakenly trust it. The Denning-Sacco protocol mitigates this by mandating timestamps within")
        print("the ticket, empowering Bob to instantly discard replays that fall outside a viable time window.")

if __name__ == '__main__':
    main()
