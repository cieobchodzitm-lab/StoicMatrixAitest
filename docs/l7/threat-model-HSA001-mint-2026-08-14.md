# Threat Model — HSA-001 Virtue Passport Mint

**Date:** 2026-08-14

## Główne wektory

- Spoofing fingerprint / virtue score
- Replay starych autoryzacji
- Scope-creep (za szerokie uprawnienia)
- Plutocratic farming (kupowanie score)
- Przechwycenie authority
- Injection złośliwych metadanych
- Bypass warstwy L4

## Mitygacje już w artefaktach

- PDA jako jedyna authority mint/update
- Wymagany virtue_score ≥ threshold
- Untrusted zabroniony na mainnet_locked
- Eventy z audit_ref dla monitoringu

## Residual (REQUIRE_HUMAN przed Mainnet)

1. Mapowanie Council 7/11 → klucz programu
2. Dokładne CPI Metaplex Core
3. Źródło attestation virtue score

*Threat model under defender-scout.*
