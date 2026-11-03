"""Small deterministic provenance gate for narrative benchmark topics."""
from .core import Claim, Provenance, extract_claims, match, gate

__all__ = ["Claim", "Provenance", "extract_claims", "match", "gate"]
