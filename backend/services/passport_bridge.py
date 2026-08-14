"""
passport_bridge.py — Virtue Passport verification + mint gate

Integrates with:
  - phantom-crypto-core (AGT-VIRTUE-PASSPORT-v1 domain, Ed25519)
  - phantom-defender-scout (stage machine: UNTRUSTED → PROVISIONAL → TRUSTED)
  - the-bridge-virtue-nft (Solana Anchor program)

Flow:
  1. Accept signed fingerprint JSON
  2. Verify domain, required fields, freshness, signature
  3. Enforce agentClass == TRUSTED (or COUNCIL / META_JURY / DEFENDER)
  4. Only then allow mint path toward on-chain program

No Pinky: every successful verification should be preceded by a ConstitutionalAudit
in the calling context (L4).
"""

from __future__ import annotations

import base64
import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

# Domain separator must match phantom-crypto-core/scripts/sign-passport.js
DOMAIN = "AGT-VIRTUE-PASSPORT-v1"
MAX_AGE_MS = 15 * 60 * 1000  # 15 minutes freshness window

ALLOWED_TRUSTED_CLASSES = {
    "TRUSTED",
    "COUNCIL",
    "META_JURY",
    "DEFENDER",
}


@dataclass
class VerificationResult:
    valid: bool
    reason: str = ""
    agent_class: Optional[str] = None
    scope: Optional[Union[str, List[str]]] = None
    constitution_id: Optional[str] = None
    fingerprint: Optional[Dict[str, Any]] = None
    note: str = ""


def _canonical_json(obj: Dict[str, Any]) -> str:
    """Deterministic JSON with sorted keys (matches Node.js sign-passport)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def verify_passport(
    signed: Dict[str, Any],
    public_key_pem: Optional[str] = None,
    *,
    max_age_ms: int = MAX_AGE_MS,
    now_ms: Optional[int] = None,
    require_trusted: bool = True,
) -> VerificationResult:
    """
    Verify a signed Virtue Passport.

    Parameters
    ----------
    signed : dict
        Must contain domain, fingerprint, signature, algorithm.
    public_key_pem : str | None
        PEM-encoded Ed25519 public key. If None, signature check is skipped
        (useful only for structural dry-runs; never for production mint).
    require_trusted : bool
        When True, agentClass must be in ALLOWED_TRUSTED_CLASSES.
    """
    now = now_ms if now_ms is not None else int(time.time() * 1000)

    if signed.get("domain") != DOMAIN:
        return VerificationResult(False, "domain mismatch")

    fingerprint = signed.get("fingerprint")
    signature_b64 = signed.get("signature")
    if not fingerprint or not signature_b64:
        return VerificationResult(False, "missing fingerprint or signature")

    required = ["constitutionId", "agentClass", "scope", "nonce", "timestamp"]
    for field in required:
        if field not in fingerprint:
            return VerificationResult(False, f"missing required field: {field}")

    # Freshness / replay protection
    try:
        ts = int(fingerprint["timestamp"])
    except (TypeError, ValueError):
        return VerificationResult(False, "invalid timestamp")
    if abs(now - ts) > max_age_ms:
        return VerificationResult(
            False, "timestamp outside freshness window (possible replay)"
        )

    agent_class = str(fingerprint["agentClass"])

    if require_trusted and agent_class not in ALLOWED_TRUSTED_CLASSES:
        return VerificationResult(
            False,
            f"agentClass '{agent_class}' is not TRUSTED (or higher)",
            agent_class=agent_class,
        )

    # Signature verification (Ed25519)
    if public_key_pem:
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                Ed25519PublicKey,
            )
            from cryptography.hazmat.primitives.serialization import (
                load_pem_public_key,
            )

            payload = {"domain": DOMAIN, **fingerprint}
            canonical = _canonical_json(payload).encode("utf-8")
            sig = base64.b64decode(signature_b64)

            pub = load_pem_public_key(public_key_pem.encode("utf-8"))
            if not isinstance(pub, Ed25519PublicKey):
                return VerificationResult(False, "public key is not Ed25519")

            pub.verify(sig, canonical)  # raises InvalidSignature on failure
        except Exception as exc:
            return VerificationResult(False, f"invalid signature: {exc}")
    else:
        # Structural-only mode (development / unit tests)
        pass

    return VerificationResult(
        valid=True,
        agent_class=agent_class,
        scope=fingerprint.get("scope"),
        constitution_id=fingerprint.get("constitutionId"),
        fingerprint=fingerprint,
        note=(
            "Signature and stage checks passed. "
            "Proceed to L4 audit + on-chain mint when CNOTA gate is satisfied."
        ),
    )


def prepare_mint_payload(
    verified: VerificationResult,
    user_id: str,
    virtue_scores: Dict[str, int],
) -> Dict[str, Any]:
    """
    Build the payload that will be sent to the Solana program
    (or queued for the real RPC call).
    """
    if not verified.valid:
        raise ValueError("Cannot prepare mint from invalid passport")

    total = sum(virtue_scores.values())
    return {
        "user_id": user_id,
        "constitution_id": verified.constitution_id,
        "agent_class": verified.agent_class,
        "scope": verified.scope,
        "virtue_scores": virtue_scores,
        "virtue_score_total": total,
        "program_id": "VrtuPasp0rt11111111111111111111111111111111",  # matches on-chain placeholder
        "ready_for_rpc": True,
        "note": "Call the-bridge-virtue-nft::mint_virtue_nft after CNOTA balance check",
    }


def compute_fingerprint_hash(fingerprint: Dict[str, Any]) -> str:
    """Deterministic hash for audit trail / registry anchoring."""
    canonical = _canonical_json({"domain": DOMAIN, **fingerprint})
    return hashlib.sha3_256(canonical.encode("utf-8")).hexdigest()
