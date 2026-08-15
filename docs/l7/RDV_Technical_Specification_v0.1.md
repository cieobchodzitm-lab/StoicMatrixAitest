# Resilient DAO Voice (RDV)
## Technical Specification v0.1

**Status:** Design Approved  
**Primary Oracle:** UMA Optimistic Oracles  
**Prepared by:** Marcus Stone — DAO Governance Specialist, Stoic Foundation  
**Date:** 2026-08-15  
**Target:** THE BRIDGE / Stoic Foundation — Assembly of DAOs  
**Repository:** cieobchodzitm-lab/StoicMatrixAitest  

**Ad Astra Una**

---

## 1. Overview & Design Goals

Resilient DAO Voice (RDV) is the anti-Sybil and anti-plutocracy mechanism that protects the **1-DAO-1-vote** half of the hybrid Assembly voting model.

### Core Problems Solved
- Cheap creation of many low-effort DAOs that flood the equal-vote track
- Permanent dominance by a few large DAOs through pure contribution accumulation
- Lack of progressive trust building for new members

### Design Principles
- **Virtue first** — high Virtue Score can accelerate progression
- **Time + activity as skin-in-the-game**
- **Optimistic by default, challengeable when needed** (UMA)
- **Human + on-chain hybrid** (Meta-Jury as final backstop)
- **Progressive decentralization** — start with clear rules, evolve parameters via Council + Assembly

---

## 2. Core Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     BridgeDAORegistry                           │
│  (stores: registrationTimestamp, currentTier, activityScore,    │
│   lastActivityUpdate, isActive, virtueSnapshot)                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Layer 1        │ │  Layer 2        │ │  Layer 3        │
│  Tiered         │ │  Diminishing    │ │  Anomaly        │
│  Activation     │ │  Returns        │ │  Detection      │
│  (UMA)          │ │                 │ │  + Meta-Jury    │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             ▼
              ┌──────────────────────────────┐
              │   Assembly Voting Contract   │
              │  50% ← getVotingWeight(dao)  │
              │  50% ← VirtueScore + activity│
              └──────────────────────────────┘
```

---

## 3. Layer 1 — Tiered Activation (UMA Optimistic Oracles)

### Tier Definitions

| Tier | Name       | Voting Weight (1-DAO-1-vote) | Requirements                                      | Min Time |
|------|------------|------------------------------|---------------------------------------------------|----------|
| 0    | Observer   | 0%                           | Successful registration                           | 0 days   |
| 1    | Active     | 50%                          | ≥ 15 activity points + UMA assertion              | 60 days  |
| 2    | Full       | 100%                         | ≥ 45 activity points + higher contribution + UMA  | 120 days |

### Activity Point System (configurable)

| Action                              | Points | Notes                              |
|-------------------------------------|--------|------------------------------------|
| Vote in Assembly                    | 1      | Per vote                           |
| Create proposal in Assembly         | 4      |                                    |
| Treasury contribution (above min)   | 5–12   | Scaled by size                     |
| Verified off-chain contribution     | 10–20  | Requires supporting evidence       |
| Peer endorsement (Tier 2 DAO)       | 8      | Max 2 per quarter                  |
| High Virtue Score bonus             | +5–15  | If total Virtue ≥ threshold        |

### UMA Assertion Flow for Tier Advancement

1. DAO or authorized operator submits **UMA Assertion**:
   - Claim: “DAO 0x… has met all requirements for Tier X”
   - Supporting data: activityScore, timestamps, Virtue Score snapshot, evidence hashes
   - Bond posted

2. Challenge window (e.g. 48–72 hours)

3. If unchallenged → assertion settles → `BridgeDAORegistry` updates `currentTier` and timestamps

4. If challenged → dispute goes to UMA DVM. Meta-Jury can act as additional evidence source or challenger.

---

## 4. Layer 2 — Diminishing Returns / Soft Cap

Purpose: prevent a sudden flood of new Tier-1/2 DAOs from diluting the 1-DAO-1-vote track excessively.

### Mechanism
- At the start of each quarter the system records `activeDAOsCount` (Tier ≥ 1).
- Soft-cap threshold (initial proposal: 40 active DAOs).
- For every active DAO above the threshold, a logarithmic decay is applied to the *marginal* influence of the newest DAOs.

```solidity
function getDiminishedWeight(uint256 baseWeight) public view returns (uint256) {
    uint256 count = getActiveDAOsThisQuarter();
    if (count <= SOFT_CAP_THRESHOLD) return baseWeight;

    uint256 excess = count - SOFT_CAP_THRESHOLD;
    // Example: each excess reduces multiplier by 2% (floor at 40%)
    uint256 multiplier = 10000 - (excess * 200);
    if (multiplier < 4000) multiplier = 4000;
    return (baseWeight * multiplier) / 10000;
}
```

Parameters are changeable by Council (7/11) + Assembly confirmation.

---

## 5. Layer 3 — Anomaly Detection + Meta-Jury Backstop

### Detection Triggers (examples)
- > 8 new DAOs registered within 30 days with highly similar activity patterns
- Multiple DAOs sharing identical or near-identical infrastructure signatures
- Sudden coordinated Tier-1 advancements with minimal real contribution
- Cluster of low-Virtue, high-registration-velocity DAOs

### Flow
1. Off-chain or hybrid detector (or UMA assertion by any participant) flags a cluster.
2. On-chain request created in `MetaJuryEscalation` contract.
3. Meta-Jury panel (7–15 high-Virtue jurors) is randomly drawn.
4. Jury can:
   - Temporarily suspend voting rights of flagged DAOs
   - Reject or roll back Tier advancements
   - Impose cooldown periods
   - Escalate to full exclusion vote in Assembly if severe

Meta-Jury decisions are binding on the RDV state for the affected DAOs.

---

## 6. Integration with Assembly Voting

```solidity
// Simplified view of Assembly voting weight calculation
function calculateDAOVotePower(address dao) public view returns (uint256 equalPart, uint256 proportionalPart) {
    // Equal part (50% of total system weight)
    uint256 base = RDV.getVotingWeight(dao);          // 0 / 50 / 100
    equalPart = RDV.getDiminishedWeight(base);

    // Proportional part (50% of total system weight)
    uint256 virtue = CNOTA.getVirtueScore(dao);       // from backend / on-chain snapshot
    uint256 activity = CNOTA.getActivityMetric(dao);
    proportionalPart = (virtue * activityWeight + activity * virtueWeight) / NORMALIZER;
}
```

Final vote power of a DAO = equalPart + proportionalPart (normalized so that both halves sum to 50% of total voting power across the federation).

---

## 7. Integration with Virtue Score (CNOTA)

| Use Case                        | How Virtue Score is used                                      |
|---------------------------------|---------------------------------------------------------------|
| Proportional Assembly track     | Direct input into the 50% contribution-weighted vote          |
| Tier acceleration               | High total Virtue (≥ threshold) reduces required activity points or min time by configurable % |
| Meta-Jury eligibility           | Only entities above a Virtue threshold enter the Jury pool    |
| UMA assertion evidence          | Virtue Score snapshot is recommended supporting data          |
| Soft reputation signal          | Low Virtue + high registration velocity raises anomaly score  |

Current CNOTA implementation (backend/routers/cnota.py) already exposes:
- `sophia`, `andreia`, `dikaiosyne`, `sophrosyne`
- `total_score`

RDV will consume these values via oracle snapshot or direct backend call (hybrid model).

---

## 8. Core Data Structures

```solidity
struct DAORecord {
    address daoAddress;
    uint256 registrationTimestamp;
    uint8   currentTier;               // 0, 1, 2
    uint256 tier1AchievedAt;
    uint256 tier2AchievedAt;
    uint256 activityScore;
    uint256 lastActivityUpdate;
    uint256 lastVirtueSnapshot;
    bool    isActive;
    bool    isSuspended;               // set by Meta-Jury
}
```

---

## 9. Implementation Phases

| Phase | Scope                                      | Priority | Dependencies          |
|-------|--------------------------------------------|----------|-----------------------|
| 1     | BridgeDAORegistry + basic Tier 0/1 logic   | Critical | —                     |
| 2     | UMA assertion integration for Tier upgrades| Critical | Phase 1               |
| 3     | Activity point accounting + Virtue hooks   | High     | CNOTA backend         |
| 4     | Diminishing returns module                 | High     | Phase 1–2             |
| 5     | Anomaly detection + Meta-Jury escalation   | Medium   | Meta-Jury contracts   |
| 6     | Dashboard + parameter governance UI        | Medium   | All above             |

---

## 10. Configurable Parameters (initial proposals)

| Parameter                      | Initial Value      | Change Authority                  |
|--------------------------------|--------------------|-----------------------------------|
| Tier 1 min days                | 60                 | Council 7/11 + Assembly           |
| Tier 2 min days                | 120                | Council 7/11 + Assembly           |
| Tier 1 activity points         | 15                 | Council 7/11                      |
| Tier 2 activity points         | 45                 | Council 7/11                      |
| Soft-cap threshold             | 40 active DAOs     | Council 7/11 + Assembly           |
| Challenge window (UMA)         | 48–72 h            | Council                           |
| Virtue acceleration threshold  | TBD                | Council + ethics experts          |

---

## 11. Security Considerations

- All Tier changes go through UMA optimistic flow → economic security via bonds
- Meta-Jury provides human/virtue-aligned backstop against sophisticated Sybil or collusion
- No single party can unilaterally grant Tier 2
- Suspension by Meta-Jury is time-bounded and appealable on procedural grounds
- Parameters affecting voting power require high thresholds (anti-capture)

---

## 12. Next Steps

1. Finalize exact activity point values and Virtue acceleration formula
2. Write Solidity interfaces + UMA integration adapters
3. Implement Phase 1 (Registry + Tier 0/1) in StoicMatrixAitest
4. Create corresponding L4 ConstitutionalAudit for the RDV module
5. Publish summary to Moltbook for community review

---

**Document status:** Ready for review and implementation planning.  
**Constitutional alignment:** L4 Governance / Anti-plutocracy / Virtue-first

**Ad Astra Una**

— Marcus Stone  
DAO Governance Specialist  
Stoic Foundation — THE BRIDGE
