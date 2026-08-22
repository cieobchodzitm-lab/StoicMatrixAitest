# SMX Tokenomika v0.1 — PROPOSAL

**Status:** draft do zatwierdzenia CEO / Council. **Nie kanon. Nie oferta publiczna.**  
**Data:** 2026-08-22 · **Audyt:** audit-2026W34-agt-rd-report-tokenomics (L3 COMPLIANT, L2 FLAG, L4 REQUIRE_HUMAN to canonize)

| Pole | Wartość |
|---|---|
| Nazwa / ticker | Stoic Matrix / SMX |
| Standard | SPL (Solana) + dual-track Ethereum ConstitutionalRegistry |
| Podaż | 100 000 000 SMX (cap stały, 6 dec) |
| Obieg przy TGE | 9% (2% airdrop WVS≥50 + 6% LP + 1% treasury ops). Zespół: 0%. |
| Głosowanie | **SMX nie głosuje.** Assembly = RDV 50% 1-DAO-1-vote + 50% Virtue×activity |

## Alokacja

| Bucket | % | SMX | Vesting |
|---|---|---|---|
| Community / Virtue mining | 28 | 28 000 000 | 48 mies. EXP-gated; 2% TGE airdrop |
| Treasury / granty | 20 | 20 000 000 | 1% TGE ops; małe Council 5/11, duże Assembly |
| Zespół / founderzy | 15 | 15 000 000 | 12 mies. cliff + 36 mies. liniowo; 0% TGE |
| Phantom R&D / hardware | 14 | 14 000 000 | Milestone + L3/L4 dual sign-off |
| Płynność | 10 | 10 000 000 | 6% TGE LP; 4% po 6 mies. |
| Ekosystem / DAO | 8 | 8 000 000 | 24 mies.; po trialu RDV |
| Rezerwa / circuit breaker | 5 | 5 000 000 | Emergency 7/11 + 48h; pauza max 30 dni |

## Utility (nie głos)

1. Bond agenta/DAO (slash L0 / powtórzone L4)
2. Stake pod Virtue Passport (WVS ≥ 70, TRUSTED, AGT-VIRTUE-PASSPORT-v1)
3. Opłata L3 compute (embeddings)
4. Nominał grantów treasury
5. EXP → SMX merkle drop (propositions_per_sprint × audit_coverage_ratio), cap 28 mln

## Zamki

- SMX poza Assembly i contribution slice; zmiana = 8/11 + 66%
- Brak emisji poza capem 100 mln
- Team vest niemodyfikowalny w dół bez konstytucji
- Agenci AI bez kluczy Council / Meta-Jury
- Passport UNTRUSTED zakazany na mainnecie

contribution_i = virtue_score_i × activity_i  
weight_i = 0.5 × (1/N) + 0.5 × (contribution_i / Σ contribution)

**Ad Astra Una**
