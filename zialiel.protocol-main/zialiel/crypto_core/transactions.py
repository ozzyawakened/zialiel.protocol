
import hashlib
import time
import json
from dataclasses import dataclass, field, asdict

@dataclass
class Transaction:
    sender: str
    recipient: str
    amount: int
    fee: int
    id: str = field(default_factory=lambda: hashlib.sha256(str(time.time()).encode()).hexdigest())
    timestamp: float = field(default_factory=time.time)
    signature: bytes = b''

    def to_message(self) -> bytes:
        """
        Creates a canonical, signable representation of the transaction.
        The signature itself is excluded from the message.
        """
        d = asdict(self)
        # Exclude the signature for the message to be signed
        d.pop('signature', None)
        # Sort keys for a consistent order
        return json.dumps(d, sort_keys=True).encode()

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the transaction."""
        return asdict(self)

    def calculate_hash(self) -> str:
        """Calculates the hash of the transaction's signable message."""
        return hashlib.sha256(self.to_message()).hexdigest()
