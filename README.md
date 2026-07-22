# A Comprehensive Survey on Post-Quantum Cryptography Migration

**Author:** Allan Douglas Costa  
**Affiliation:** Institute of Cyberspace (ICIBE), Federal Rural University of the Amazon (UFRA), Belém, Brazil  
**E-mail:** allan.costa@ufra.edu.br  
**ORCID:** [0000-0002-7068-8889](https://orcid.org/0000-0002-7068-8889)  
**Target venue:** IEEE Communications Surveys & Tutorials (IF ~35)  
**Status:** Manuscript in preparation — July 2026

---

## Full Title

> *A Comprehensive Survey on Post-Quantum Cryptography Migration: Standards, Threat Models, Implementation Challenges, and Regulatory Roadmaps for Legacy Systems*

---

## Abstract

The imminent realization of fault-tolerant quantum computers threatens to render RSA and elliptic-curve cryptography (ECC) fundamentally insecure. This survey provides a unified taxonomy of PQC migration challenges spanning six critical infrastructure domains — TLS/Web PKI, Public Key Infrastructure, Internet of Things (IoT), Industrial Control Systems (ICS/OT), Blockchain/DLT, and VPN/Zero Trust Network Access — synthesizing 151 peer-reviewed publications and 39 normative documents. A Migration Readiness Classification (MRC) framework is proposed to classify legacy systems across four readiness tiers using three weighted dimensions: cryptographic exposure, upgrade feasibility, and regulatory deadline proximity. Cross-regulatory gap analysis compares NIST, NSA CNSA 2.0, ENISA, GDPR, and LGPD requirements with sector-specific compliance timelines.

---

## Repository Structure

```
.
├── pqc_survey_main.tex          # Main LaTeX manuscript (IEEEtran)
├── pqc_survey.bib               # BibTeX bibliography (~236 entries)
├── delphi_mrc_validation.tex    # Delphi+AHP weight validation subsection
├── pqc_survey_main.pdf          # Compiled PDF (25 pages, latest build)
├── requirements.txt             # Python dependencies
│
├── data/                        # Corpus and search data
│   ├── corpus_peer_reviewed.csv         # 151 peer-reviewed papers (annotated)
│   ├── corpus_normative.csv             # 39 normative/standards documents
│   ├── prisma_selection.csv             # PRISMA screening decisions
│   ├── dedup_log.csv                    # Deduplication audit log
│   ├── search_protocol.md               # Systematic search protocol
│   ├── mrc_delphi_instrument.md         # Delphi survey instrument (LLM-simulated)
│   └── partial_systematic_search_record_2026-07-16.md
│
├── figures/                     # All manuscript figures
│   ├── *.pdf                    # Final figures (included by manuscript)
│   └── tikz/                    # TikZ source files for diagrams
│       ├── hybrid_tls_sequence_tikz.tex
│       ├── prisma_flowchart_tikz.tex
│       ├── survey_overview_tikz.tex
│       └── taxonomy_diagram_tikz.tex
│
├── scripts/                     # Python analysis and figure-generation
│   ├── generate_all_figures.py  # Generates all matplotlib figures
│   ├── mrc_scorer.py            # MRC framework scoring engine
│   ├── mrc_weights_audit.py     # Weight sensitivity analysis
│   └── split_corpus.py          # Corpus split/filter utility
│
├── docs/                        # Project documentation
│   ├── AUDIT_LOG.md             # Session-by-session change log
│   └── COMPILE_INSTRUCTIONS.md  # LaTeX compilation instructions
│
└── archive/                     # Historical snapshots (reference only)
    ├── _ORIGINAL_v1/            # Original draft
    └── _CURRENT_v2/             # Pre-session-7 snapshot
```

---

## Corpus Summary

| Category | Count |
|---|---|
| Peer-reviewed papers | **151** |
| Normative / standards documents | **39** |
| **Total** | **190** |

### Peer-reviewed papers by domain

| Domain | Papers |
|---|---|
| TLS / Web PKI | ~32 |
| Public Key Infrastructure (PKI) | ~18 |
| IoT / Embedded Systems | ~28 |
| ICS / OT / SCADA | ~20 |
| Blockchain / DLT | ~19 |
| VPN / ZTNA / Zero Trust | ~14 |
| Hybrid / Post-standardization / Cross-domain | ~20 |

### Corpus CSV schema

```
record_id, title, authors, year, source_db, venue, doi, subtopic,
included, exclusion_reason, qac_score, nist_level, domain,
migration_strategy, corpus_type, peer_reviewed, audit_note
```

---

## MRC Framework

The **Migration Readiness Classification (MRC)** framework scores each domain:

```
MRC(S) = w_E * E + w_F * (1 - F) + w_D * (1 - D)
```

| Weight | Dimension | Author | Delphi R2 |
|---|---|---|---|
| w_E | Cryptographic Exposure | 0.450 | **0.471** |
| w_F | Upgrade Infeasibility | 0.350 | **0.348** |
| w_D | Deadline Distance | 0.200 | **0.181** |

**Tiers:** T1 >= 0.75 (Critical) | T2 >= 0.50 (High) | T3 >= 0.25 (Moderate) | T4 < 0.25 (Low)

| Domain | E | F | D | MRC | Tier |
|---|---|---|---|---|---|
| TLS/Web | 0.600 | 0.333 | 0.000 | 0.703 | T2 |
| PKI | 0.833 | 0.333 | 0.100 | 0.788 | **T1** |
| IoT | 0.600 | 0.500 | 0.200 | 0.605 | T2 |
| ICS/OT | 0.750 | 0.500 | 0.500 | 0.613 | T2 |
| Blockchain | 0.600 | 0.400 | 0.200 | 0.640 | T2 |
| VPN/ZTNA | 0.750 | 0.000 | 0.000 | 0.888 | **T1** |

---

## Delphi+AHP Weight Validation

A two-round Delphi study using **LLM-simulated expert personas** (n=7) validated the MRC weights. File: `delphi_mrc_validation.tex`. Instrument: `data/mrc_delphi_instrument.md`.

### Expert panel

| ID | Profile | Primary lens |
|---|---|---|
| E1 | CISO, Fortune-500 financial institution | PKI/TLS; data-sensitivity |
| E2 | NIST PQC standardisation contributor | Algorithm feasibility |
| E3 | ICS/OT security architect, power utility | Operational feasibility |
| E4 | IoT security researcher, embedded systems | Hardware-constrained migration |
| E5 | Cloud security engineer, hyperscaler | TLS/VPN at scale |
| E6 | Blockchain/DLT security specialist | Consensus-layer migration |
| E7 | Academic PQC researcher | Balanced/theoretical |

### AHP aggregated results

| Round | w_E | w_F | w_D | CR |
|---|---|---|---|---|
| Author baseline | 0.450 | 0.350 | 0.200 | — |
| Round 1 | 0.459 | 0.367 | 0.174 | 0.003 |
| **Round 2** | **0.471** | **0.348** | **0.181** | **0.004** |

- **Kendall's W = 0.43** (chi2 = 6.00, p < 0.05) — moderate-to-good concordance
- Maximum delta from author weights: 2.1 percentage points
- **All 6 domains are tier-stable** across all 4 weight x sub-score scenarios (no tier changes)

> **Caveat:** All responses are LLM-simulated, conditioned on stated profiles. This is a *structured heuristic consensus*, not empirically collected human-panel data. Replication with 14-19 real PQC practitioners is identified as future work (Open Challenge G7).

---

## Systematic Search

Partial public-database search executed on **2026-07-16**:

| Database | Access | Executed |
|---|---|---|
| arXiv cs.CR | Open | Yes |
| IACR ePrint | Open | Yes |
| Google Scholar | Partial | Yes |
| IEEE Xplore | Restricted | Indirect only |
| ACM Digital Library | Restricted | Indirect only |
| Scopus / Web of Science | Restricted | Pending |

~130 records inspected; 12 retained after screening; 7 were new candidates.

Full log: `data/partial_systematic_search_record_2026-07-16.md`  
Search strings and protocol: `data/search_protocol.md`

> Full institutional database retrieval (IEEE Xplore, ACM DL, Scopus, WoS) is planned as future work.

---

## How to Compile

### Tectonic (recommended — single command, auto-downloads packages)

```bash
# Install: https://tectonic-typesetting.github.io/
tectonic pqc_survey_main.tex
```

Tectonic handles multiple passes and BibTeX automatically.

### Docker (TeX Live)

```bash
docker run --rm -v "$(pwd)":/workspace -w /workspace texlive/texlive:latest bash -c \
  "pdflatex pqc_survey_main.tex && \
   bibtex pqc_survey_main && \
   pdflatex pqc_survey_main.tex && \
   pdflatex pqc_survey_main.tex"
```

### Local TeX Live 2024+

```bash
pdflatex pqc_survey_main.tex
bibtex pqc_survey_main
pdflatex pqc_survey_main.tex
pdflatex pqc_survey_main.tex
```

Required packages: `IEEEtran`, `hyperref`, `booktabs`, `mdframed`, `enumitem`, `tikz`, `pgfplots`, `placeins`, `algorithm`, `algorithmicx`.  
See `docs/COMPILE_INSTRUCTIONS.md` for full details.

---

## How to Run Scripts

```bash
pip install -r requirements.txt

python scripts/generate_all_figures.py   # All matplotlib figures
python scripts/mrc_scorer.py             # MRC scoring for a domain
python scripts/mrc_weights_audit.py      # Weight sensitivity analysis
```

---

## AI Disclosure

This manuscript was prepared with assistance from Claude (Anthropic) for literature search, LaTeX editing, BibTeX management, figure generation, and the LLM-simulated Delphi study. All scientific claims, analysis, interpretation, and conclusions are the sole responsibility of the author. The LLM-simulated Delphi is explicitly labeled throughout and is not presented as empirical human-panel data.

---

## Funding

Amazon Foundation for the Support of Studies and Research (FAPESPA), Information and Communication Technology Company of the State of Pará (PRODEPA), and the National Education and Research Network (RNP).

---

## License

Manuscript text and figures: copyright of the author.  
Analysis code (`scripts/`): MIT License.  
Corpus data (`data/*.csv`): CC BY 4.0.
