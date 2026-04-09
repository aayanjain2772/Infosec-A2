import json

class KeyDistributionCenter:
    def __init__(self):
        self.keys = {"Alice": "KA", "Bob": "KB"}

    def request_session(self, initiator, target, nonce1):
        print(f"[KDC] Received request from {initiator} to communicate with {target} (Nonce: {nonce1})")
        session_key = "K_AB_SESSION"
        
        # Ticket to Bob encrypted with Bob's key
        ticket_to_bob = {"session_key": session_key, "initiator": initiator}
        encrypted_ticket = f"ENC_KB({json.dumps(ticket_to_bob)})"
        
        # Response to Alice encrypted with Alice's key
        response_to_alice = {
            "nonce1": nonce1,
            "target": target,
            "session_key": session_key,
            "ticket_to_bob": encrypted_ticket
        }
        print(f"[KDC] Sending session key and ticket to {initiator}")
        return f"ENC_KA({json.dumps(response_to_alice)})", encrypted_ticket

class Node:
    def __init__(self, name):
        self.name = name

    def decrypt(self, encrypted_msg):
        # Simplify decryption logic for demonstration purposes
        try:
            start_idx = encrypted_msg.find('(') + 1
            end_idx = encrypted_msg.rfind(')')
            payload = encrypted_msg[start_idx:end_idx]
            return json.loads(payload)
        except Exception as e:
            print(f"[{self.name}] Failed to decrypt: {e}")
            return None

def normal_protocol():
    print("=== Needham-Schroeder Normal Protocol Execution ===")
    kdc = KeyDistributionCenter()
    alice = Node("Alice")
    bob = Node("Bob")
    
    nonce1 = "N1"
    response_from_kdc, ticket = kdc.request_session(alice.name, bob.name, nonce1)
    
    decrypted_response = alice.decrypt(response_from_kdc)
    print(f"[Alice] Decrypted KDC response, verified N1: {decrypted_response['nonce1']} == {nonce1}")
    session_key = decrypted_response['session_key']
    ticket_to_bob = decrypted_response['ticket_to_bob']
    
    print(f"[Alice] Sending ticket to Bob...")
    decrypted_ticket = bob.decrypt(ticket_to_bob)
    print(f"[Bob] Decrypted ticket. Session key: {decrypted_ticket['session_key']} from {decrypted_ticket['initiator']}")
    
    nonce2 = "N2"
    msg_to_alice = f"ENC_KAB({nonce2})"
    print(f"[Bob] Sending challenge {msg_to_alice} to Alice")
    
    response_to_bob = f"ENC_KAB({nonce2}-1)"
    print(f"[Alice] Sending response {response_to_bob} back to Bob")
    print(f"[Bob] Verified response. Mutual authentication successful.\n")
    return session_key, ticket_to_bob

def denning_sacco_attack(hijacked_session_key, intercepted_ticket_to_bob):
    print("=== Denning-Sacco Attack Execution ===")
    print("Mallory has compromised an old session key and its corresponding ticket to Bob.")
    
    mallory = Node("Mallory")
    bob = Node("Bob")
    
    print(f"[Mallory] Replaying old ticket to Bob: {intercepted_ticket_to_bob}")
    decrypted_ticket = bob.decrypt(intercepted_ticket_to_bob)
    print(f"[Bob] Decrypted ticket. Session key: {decrypted_ticket['session_key']} from {decrypted_ticket['initiator']}")
    
    nonce_bob = "N_BOB_NEW"
    msg_to_alice = f"ENC_KAB({nonce_bob})"
    print(f"[Bob] Sending challenge {msg_to_alice} to Alice (intercepted by Mallory)")
    
    response = f"ENC_KAB({nonce_bob}-1)"
    print(f"[Mallory] Sending valid response {response} using the compromised session key")
    
    print(f"[Bob] Verified response. Bob incorrectly believes he is securely communicating with Alice!")

def main():
    session_key, ticket = normal_protocol()
    
    print("\n--- Time passes. The session key 'K_AB_SESSION' is now stale and was found by Mallory ---\n")
    denning_sacco_attack(session_key, ticket)
    
    print("\n=== Mitigation ===")
    print("The Denning-Sacco attack is possible because the Needham-Schroeder protocol does not use timestamps.")
    print("Without timestamps, Bob has no way of knowing if the ticket is fresh or an old replay.")
    print("Mitigation: Include timestamps in tickets (like in Kerberos) so participants can reject old tickets.")

if __name__ == '__main__':
    main()
