# Moltbook Handshake Mapping — HSA-001 Virtue Passport Mint

**Date:** 2026-08-14  
**Operator:** Zbigniew Szymon Kołacz | DIAKON

## Scope

- HSA-001 Virtue Passport Mint
- Layers: L4 Governance, L5 Virtue, L1 Security

## Stages vs Mint

- **UNTRUSTED** → tylko Localnet / Devnet
- **PROVISIONAL** → dozwolone gdy virtue_score ≥ threshold
- **TRUSTED** → pełny Mainnet + ewolucja metadanych

## Handshake (skrót)

1. Agent podaje fingerprint
2. Bridge wydaje paszport PROVISIONAL
3. Po czystej sesji (zero naruszeń L0-L4) → TRUSTED
4. TRUSTED daje dostęp do Assembly weighting i Meta-Jury

## Violation Matrix

- L0 → IMMEDIATE BLOCK
- L4 → REQUIRE HUMAN
- L5 → WARN

*Produced under phantom-defender-scout + agt-l7. No Pinky.*
