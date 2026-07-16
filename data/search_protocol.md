# Systematic Search Protocol
## PQC Migration Survey — IEEE Communications Surveys & Tutorials

**Document version:** 1.0  
**Date:** July 2026  
**Status:** Documented and ready for execution in indexed databases

---

## 1. Research Questions Driving the Search

- RQ1: What migration strategies have been proposed for PQC adoption across TLS, PKI, IoT, ICS/OT, Blockchain, and VPN/ZTNA?
- RQ2: What implementation challenges does PQC introduce in resource-constrained and legacy environments?
- RQ3: How do regulatory frameworks across the US, EU, and Brazil align or diverge on PQC migration timelines?
- RQ4: What framework can classify legacy systems by migration urgency?

---

## 2. Search Strings

### Primary string (all databases)

```
("post-quantum cryptography" OR "post-quantum cryptographic" OR "quantum-resistant cryptography"
 OR "lattice-based cryptography" OR "code-based cryptography" OR "hash-based signatures"
 OR "ML-KEM" OR "ML-DSA" OR "SLH-DSA" OR "CRYSTALS-Kyber" OR "CRYSTALS-Dilithium"
 OR "SPHINCS+" OR "FALCON" OR "HQC" OR "BIKE" OR "NTRU")
AND
("migration" OR "transition" OR "deployment" OR "implementation" OR "integration"
 OR "performance" OR "benchmark" OR "overhead" OR "feasibility")
AND
("TLS" OR "SSL" OR "PKI" OR "X.509" OR "certificate" OR "IoT" OR "Internet of Things"
 OR "embedded" OR "microcontroller" OR "ICS" OR "SCADA" OR "OT" OR "blockchain"
 OR "VPN" OR "IPsec" OR "Zero Trust" OR "ZTNA" OR "enterprise")
```

### Secondary string (regulatory and roadmap focus)

```
("post-quantum" OR "quantum-safe" OR "quantum-resistant")
AND
("regulatory" OR "compliance" OR "mandate" OR "NIST" OR "NSA" OR "CNSA" OR "ENISA"
 OR "migration roadmap" OR "transition plan" OR "crypto-agility" OR "cryptographic agility")
```

### Tertiary string (2024-2026 post-standardization focus)

```
("FIPS 203" OR "FIPS 204" OR "FIPS 205" OR "FIPS 206" OR "ML-KEM" OR "ML-DSA" OR "SLH-DSA"
 OR "FN-DSA" OR "HQC" OR "post-quantum standard")
AND
("implementation" OR "deployment" OR "performance" OR "migration" OR "evaluation")
```

---

## 3. Databases to Search

| Database | Coverage | Access | Status |
|---|---|---|---|
| IEEE Xplore | IEEE/IET journals and conferences | Institutional login | Pending execution |
| ACM Digital Library | ACM journals and conferences | Institutional login | Pending execution |
| Scopus | Multi-disciplinary, 25,000+ journals | Institutional login | Pending execution |
| Web of Science | Multi-disciplinary, 21,000+ journals | Institutional login | Pending execution |
| NIST CSRC | FIPS, SP, IR documents | Public | Executed (normative corpus) |
| IACR ePrint | Cryptography preprints | Public | Supplementary only |

---

## 4. Inclusion and Exclusion Criteria

### Inclusion (ALL must be true)

| # | Criterion |
|---|---|
| I1 | Published in peer-reviewed venue (journal, conference with review committee, or workshop with proceedings) |
| I2 | Published 2014-2026 (seminal pre-2014 works considered individually) |
| I3 | Addresses at least one of: PQC algorithm analysis, PQC implementation, PQC migration, PQC in specific domain |
| I4 | Available in English |
| I5 | Full text accessible for data extraction |

### Exclusion (ANY is sufficient to exclude)

| # | Criterion |
|---|---|
| E1 | Non-peer-reviewed: arXiv without accepted venue, blog post, white paper, manufacturer datasheet |
| E2 | Purely theoretical without connection to migration or implementation |
| E3 | Surveys/reviews already superseded by a more complete version by the same group |
| E4 | Duplicate (same content as another included paper, different venue) |
| E5 | Focus exclusively on symmetric cryptography (AES, SHA) without PQC asymmetric context |
| E6 | Classical cryptanalysis without quantum threat model |

---

## 5. Data Extraction Fields

For each included paper:

```
record_id, title, authors, year, source_db, venue, doi, subtopic, included,
exclusion_reason, qac_score, nist_level, domain, migration_strategy,
corpus_type, peer_reviewed, audit_note
```

Quality Assessment Checklist (QAC, scored 1-5):
- 5: Clear methodology, reproducible results, cited in multiple venues
- 4: Solid methodology, some reproducibility gaps
- 3: Methodology described but limited evaluation
- 2: Preliminary/workshop paper, limited evidence
- 1: Opinion/position paper, minimal evidence

Minimum QAC for inclusion: 3

---

## 6. PRISMA 2020 Flow

The following funnel represents the target search execution. Numbers in brackets
are targets based on known literature volume; actual numbers will be recorded
upon database execution.

```
Records identified via database search
IEEE Xplore: [~1,200]
ACM DL:      [~600]
Scopus:      [~900]
Web of Sci:  [~700]
Other:       [~150]
             -----------
Total:       [~3,550]

After duplicate removal:           [~2,200]

Title/abstract screening:
  Excluded (E1-E6):                [~1,900]
  Retained for full-text:          [~300]

Full-text eligibility assessment:
  Excluded (insufficient detail):  [~100]
  Excluded (no migration focus):   [~50]
  Retained peer-reviewed:          [target: 150+]

Normative/grey literature (separate corpus):
  NIST FIPS, SP, IR:               [15]
  NSA/CNSA advisories:             [4]
  ENISA reports:                   [5]
  IETF RFCs and drafts:            [8]
  Government mandates:             [7]
  Total normative:                 [39]

FINAL CORPUS:
  Peer-reviewed:   [target: 150+]
  Normative:       [39]
  Total:           [target: 189+]
```

---

## 7. Execution Log

| Date | Database | String Used | Raw Results | After Filter | Notes |
|---|---|---|---|---|---|
| [pending] | IEEE Xplore | Primary | [TBD] | [TBD] | |
| [pending] | ACM DL | Primary + Tertiary | [TBD] | [TBD] | |
| [pending] | Scopus | Primary + Secondary | [TBD] | [TBD] | |
| [pending] | Web of Science | Primary | [TBD] | [TBD] | |

---

## 8. Current Corpus Status (July 2026)

- Peer-reviewed included: 107 (72 original + 35 added Session 6)
- Normative included: 39
- Total: 146
- Gap to IEEE CST minimum: ~43 peer-reviewed papers
- Primary gap covered: TLS 2023-2025, IoT/TCHES 2025-2026, Blockchain, Crypto-Agility, ICS/OT, VPN
- Remaining gap: broader 2024-2025 Scopus/ACM DL systematic execution

Session 6 additions: 35 papers verified via web search agents across four domains
(TLS/PKI n=8, IoT/ICS n=14, VPN/Blockchain/Crypto-Agility n=10, Post-standardization n=3).
DOI_UNVERIFIED entries (record 151, 129, 130) require author/DOI confirmation
before final submission. Execution against indexed databases still pending
(institutional IEEE Xplore, ACM DL, Scopus access required).
