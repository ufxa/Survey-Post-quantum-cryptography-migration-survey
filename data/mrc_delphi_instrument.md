# MRC Weight Validation: Delphi Survey Instrument
## Migration Readiness Classification Framework
## Post-Quantum Cryptography Migration Survey

**Document version:** 1.0  
**Date:** July 2026  
**Method:** Two-round Delphi + AHP pairwise comparison  
**Target respondents:** 12-20 experts in PQC, cryptographic engineering, or enterprise security

---

## Background (for respondents)

The Migration Readiness Classification (MRC) framework scores legacy systems
on their urgency for post-quantum cryptography migration:

```
MRC(S) = w_E * E + w_F * (1 - F) + w_D * (1 - D)
```

Where:
- **E** (Exposure): fraction of system functions relying on quantum-vulnerable primitives (0-1)
- **F** (Feasibility): fraction of components requiring hardware replacement vs. firmware update (0-1, higher = harder)
- **D** (Deadline proximity): normalized regulatory deadline (0 = deadline already past, 1 = 10+ years away)

The current paper uses **author-assigned heuristic weights**: w_E = 0.45, w_F = 0.35, w_D = 0.20.

This Delphi survey aims to validate or adjust these weights through expert consensus.

---

## Round 1: Open Elicitation

### Section 1 — Expert Profile

1. Your primary area of expertise (select all that apply):
   - [ ] PQC algorithm design and analysis
   - [ ] Cryptographic engineering and implementation
   - [ ] Enterprise security architecture
   - [ ] Regulatory compliance and risk management
   - [ ] Embedded systems / IoT security
   - [ ] Industrial control system security
   - [ ] Network security (TLS, VPN, PKI)
   - [ ] Other: _______________

2. Years of experience in cryptography or information security: ___

3. Familiarity with NIST PQC standards (FIPS 203/204/205):
   - [ ] Expert (contributed to or deeply studied)
   - [ ] Advanced (regular work with PQC)
   - [ ] Intermediate (aware, some hands-on)
   - [ ] Beginner

---

### Section 2 — Dimension Importance (Free Rating)

For each dimension, assign a weight from 0 to 1 reflecting its importance
in determining **how urgently a legacy system needs PQC migration**.
Weights do not need to sum to 1 (normalization applied in analysis).

**Dimension 1: Cryptographic Exposure (E)**
How important is the fraction of a system's functions that rely on
quantum-vulnerable cryptography (RSA, ECDSA, ECDH)?

Your weight for E: _____ (0.0 to 1.0)
Justification: _______________________________________________

**Dimension 2: Upgrade Feasibility (1-F)**
How important is the difficulty of upgrading (hardware replacement vs.
firmware/software update) in determining migration urgency?

Your weight for (1-F): _____ (0.0 to 1.0)
Justification: _______________________________________________

**Dimension 3: Regulatory Deadline Proximity (1-D)**
How important is regulatory deadline proximity in driving migration urgency?

Your weight for (1-D): _____ (0.0 to 1.0)
Justification: _______________________________________________

---

### Section 3 — Pairwise Comparison (AHP Method)

For each pair of dimensions, indicate which is MORE IMPORTANT for determining
migration urgency, and by how much (use the AHP 1-9 scale below):

```
1 = Equal importance
3 = Moderate importance of one over the other
5 = Strong importance
7 = Very strong importance
9 = Extreme importance
2, 4, 6, 8 = Intermediate values
```

**Comparison 1: Exposure (E) vs. Feasibility (1-F)**
Which is more important?
- [ ] Exposure (E) by factor: _____
- [ ] Equal importance (1)
- [ ] Feasibility (1-F) by factor: _____

**Comparison 2: Exposure (E) vs. Deadline Proximity (1-D)**
Which is more important?
- [ ] Exposure (E) by factor: _____
- [ ] Equal importance (1)
- [ ] Deadline Proximity (1-D) by factor: _____

**Comparison 3: Feasibility (1-F) vs. Deadline Proximity (1-D)**
Which is more important?
- [ ] Feasibility (1-F) by factor: _____
- [ ] Equal importance (1)
- [ ] Deadline Proximity (1-D) by factor: _____

---

### Section 4 — Tier Threshold Validation

The MRC framework assigns tiers based on score:

| Tier | Score Range | Label | Action |
|---|---|---|---|
| T1 | >= 0.75 | Critical | Immediate hybrid migration |
| T2 | >= 0.50 | High | Begin migration planning |
| T3 | >= 0.25 | Medium | Monitor and assess |
| T4 | < 0.25 | Low | No immediate action |

Do you agree with these thresholds?
- [ ] Agree with all thresholds
- [ ] Disagree: T1 threshold should be _____ because: _______________
- [ ] Disagree: T2 threshold should be _____ because: _______________
- [ ] Disagree: T3 threshold should be _____ because: _______________

---

### Section 5 — Domain Score Review

The table below shows MRC scores computed with the current heuristic weights
for six infrastructure domains. Please assess face validity:

| Domain | E | F | D | MRC (current) | Tier | Your assessment |
|---|---|---|---|---|---|---|
| TLS/Web | 0.600 | 0.333 | 0.000 | 0.7033 | T2 | [ ] Valid [ ] Too high [ ] Too low |
| PKI | 0.833 | 0.333 | 0.100 | 0.7883 | T1 | [ ] Valid [ ] Too high [ ] Too low |
| IoT | 0.600 | 0.500 | 0.200 | 0.6050 | T2 | [ ] Valid [ ] Too high [ ] Too low |
| ICS/OT | 0.750 | 0.500 | 0.500 | 0.6125 | T2 | [ ] Valid [ ] Too high [ ] Too low |
| Blockchain | 0.600 | 0.400 | 0.200 | 0.6400 | T2 | [ ] Valid [ ] Too high [ ] Too low |
| VPN/ZTNA | 0.750 | 0.000 | 0.000 | 0.8875 | T1 | [ ] Valid [ ] Too high [ ] Too low |

Comments: _______________________________________________

---

## Round 2: Structured Feedback

*(Sent after Round 1 results are anonymized and aggregated)*

### Section 6 — Revision Opportunity

Round 1 results (anonymized aggregate):

| Dimension | Mean weight | Std Dev | Implied AHP weight |
|---|---|---|---|
| Exposure (E) | [TBD] | [TBD] | [TBD] |
| Feasibility (1-F) | [TBD] | [TBD] | [TBD] |
| Deadline (1-D) | [TBD] | [TBD] | [TBD] |

Given these results, do you wish to revise your weights?
- [ ] No revision: I maintain my Round 1 values
- [ ] Revise: New weights: E=___ F=___ D=___ Reason: _______________

---

## Analysis Protocol

**AHP aggregation:**
- Geometric mean of individual pairwise matrices
- Compute group priority vector
- Consistency Ratio (CR) = CI / RI; target CR < 0.10
- If group CR > 0.10, identify and resolve outlier responses

**Convergence criterion (Delphi):**
- Convergence = standard deviation < 0.05 between Round 1 and Round 2
- If not converged, conduct Round 3 (max 3 rounds)

**Output:**
- Validated weights (w_E, w_F, w_D) with 95% CI
- Group CR
- Comparison with heuristic weights (0.45, 0.35, 0.20)
- Update mrc_scorer.py if validated weights differ by >0.05 on any dimension

---

## Recruitment Target

| Profile | Target n | Recruitment channel |
|---|---|---|
| PQC algorithm researchers | 4-5 | IACR mailing list, NIST PQC workshop attendees |
| Cryptographic engineers | 3-4 | OpenSSL, liboqs, BoringSSL contributors |
| Enterprise security architects | 3-4 | (ISC)2, ISACA, RSA Conference alumni |
| Regulatory/compliance experts | 2-3 | NIST CSRC contacts, ENISA advisory |
| ICS/OT security specialists | 2-3 | ICS-CERT, ISA99 committee members |
| **Total** | **14-19** | |

---

## Timeline

| Week | Activity |
|---|---|
| 1 | Finalize instrument, IRB exemption (if applicable), recruit respondents |
| 2-3 | Round 1 open (10 days) |
| 4 | Aggregate Round 1, prepare anonymized feedback |
| 5-6 | Round 2 open (7 days) |
| 7 | Analyze convergence, compute AHP weights |
| 8 | Update paper (Section VI.B), update mrc_scorer.py |
