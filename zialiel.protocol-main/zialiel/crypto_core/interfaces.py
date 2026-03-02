
from abc import ABC, abstractmethod
from typing import Dict

class MLDSAService(ABC):
    """
    Abstract interface for a Machine Learning Digital Signature Algorithm (ML-DSA) service.
    
    This defines the contract for generating quantum-resistant keypairs, signing messages,
    and verifying signatures, allowing for interchangeable implementations.
    """

    @abstractmethod
    def generate_keypair(self) -> Dict[str, bytes]:
        """Generates a new public/private keypair."""
        pass

    @abstractmethod
    def sign(self, private_key: bytes, message: bytes) -> bytes:
        """Signs a message with the given private key."""
        pass

    @abstractmethod
    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        """Verifies a signature against a public key and message."""
        pass

    @abstractmethod
    def get_public_key_from_private_key(self, private_key: bytes) -> bytes:
        """Derives the public key from a private key."""
        pass
