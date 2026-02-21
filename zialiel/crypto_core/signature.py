# -------------------------------------
# 1. CRYPTOGRAPHIC FOUNDATION
# -------------------------------------

# ✅ REPLACEMENT: Using a real ML-DSA (Dilithium) implementation.
from dilithium import Dilithium2, ML_DSA

class SignatureScheme:
    """A wrapper for the ML-DSA (Dilithium) quantum-resistant signature scheme."""

    @staticmethod
    def generate_keys():
        """Generates a new public and private key pair."""
        pk, sk = Dilithium2.keygen()
        return pk, sk

    @staticmethod
    def sign(private_key: bytes, message: str) -> bytes:
        """Signs a message using the private key."""
        # The message needs to be bytes
        message_bytes = message.encode('utf-8')
        return Dilithium2.sign(private_key, message_bytes)

    @staticmethod
    def verify(public_key: bytes, message: str, signature: bytes) -> bool:
        """Verifies a signature using the public key."""
        message_bytes = message.encode('utf-8')
        try:
            # The verify function raises an exception on failure
            Dilithium2.verify(public_key, message_bytes, signature)
            return True
        except (ValueError, TypeError, ML_DSA.VerifyError):
            return False
