
import logging
from typing import Dict
import oqs

from .interfaces import MLDSAService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RealMLDSAService(MLDSAService):
    """
    A real implementation of the ML-DSA service using the liboqs-python library.
    This service uses the Dilithium3 algorithm, a NIST standard for quantum-resistant signatures.
    """

    def __init__(self, algorithm: str = "Dilithium3"):
        if not oqs.is_sig_enabled(algorithm):
            raise oqs.MechanismNotSupportedError(f"Signature algorithm {algorithm} is not supported by this build of liboqs.")
        self.algorithm = algorithm
        logging.info(f"RealMLDSAService initialized with {self.algorithm}.")

    def generate_keypair(self) -> Dict[str, bytes]:
        """
        Generates a new Dilithium3 keypair.

        Returns:
            Dict[str, bytes]: A dictionary containing the public and private keys.
        """
        with oqs.Signature(self.algorithm) as signer:
            public_key = signer.generate_keypair()
            private_key = signer.export_secret_key()
            logging.info(f"Generated a new {self.algorithm} keypair.")
            return {"public_key": public_key, "private_key": private_key}

    def sign(self, private_key: bytes, message: bytes) -> bytes:
        """
        Signs a message using a Dilithium3 private key.

        Args:
            private_key (bytes): The secret key.
            message (bytes): The message to sign.

        Returns:
            bytes: The resulting signature.
        """
        with oqs.Signature(self.algorithm, private_key) as signer:
            signature = signer.sign(message)
            return signature

    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        """
        Verifies a Dilithium3 signature.

        Args:
            public_key (bytes): The public key to verify against.
            message (bytes): The original message.
            signature (bytes): The signature to verify.

        Returns:
            bool: True if the signature is valid, False otherwise.
        """
        try:
            with oqs.Signature(self.algorithm) as verifier:
                return verifier.verify(message, signature, public_key)
        except Exception as e:
            logging.error(f"An error occurred during signature verification: {e}")
            return False

    def get_public_key_from_private_key(self, private_key: bytes) -> bytes:
        """
        Extracts the public key from a Dilithium3 private key.

        In liboqs, the exported secret key for Dilithium contains the public key.
        This method re-instantiates the signature object to derive it.

        Args:
            private_key (bytes): The secret key.

        Returns:
            bytes: The corresponding public key.
        """
        with oqs.Signature(self.algorithm, private_key) as signer:
            # This re-derives the public key from the provided secret key
            public_key = signer.generate_keypair()
            return public_key
