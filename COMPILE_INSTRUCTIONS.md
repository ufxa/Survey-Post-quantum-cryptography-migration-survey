# PQC Migration Survey — Build & Compile Instructions

## Quick Start (Full Build)

```bash
cd "/Users/security/Documents/Claude/Projects/Artigos/Artigo 04"

# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Generate all 8 matplotlib figures (PDFs)
cd figures && python generate_all_figures.py && cd ..

# 3. Compile TikZ standalone diagrams
pdflatex figures/taxonomy_diagram_tikz.tex
pdflatex figures/prisma_flowchart_tikz.tex
pdflatex figures/hybrid_tls_sequence_tikz.tex

# 4. Move generated PDFs to figures/output (already done by Python)
cp figures/taxonomy_diagram_tikz.pdf figures/output/taxonomy_diagram.pdf
cp figures/prisma_flowchart_tikz.pdf figures/output/prisma_flowchart.pdf
cp figures/hybrid_tls_sequence_tikz.pdf figures/output/hybrid_tls_sequence.pdf

# 5. Compile the main LaTeX survey (3 passes for cross-references)
pdflatex pqc_survey_main.tex
bibtex pqc_survey_main
pdflatex pqc_survey_main.tex
pdflatex pqc_survey_main.tex
```

The final PDF will be `pqc_survey_main.pdf`.

## Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| TeX Live 2023+ or MikTeX | LaTeX compilation | https://tug.org/texlive/ |
| Python 3.9+ | Figure generation | https://python.org |
| `IEEEtran.cls` | IEEE journal template | Included in TeX Live |
| `bibtex` | Bibliography | Included with LaTeX |

## File Structure

```
Artigo 04/
├── pqc_survey_main.tex          # Main LaTeX survey paper
├── pqc_survey.bib               # BibTeX bibliography (120 references)
├── mrc_scorer.py                # MRC framework implementation
├── requirements.txt             # Python dependencies
├── data/
│   └── prisma_selection.csv     # PRISMA 2020 selection data
└── figures/
    ├── generate_all_figures.py  # Generates Figs 1-8 (matplotlib)
    ├── taxonomy_diagram_tikz.tex     # Fig: Taxonomy (TikZ)
    ├── prisma_flowchart_tikz.tex     # Fig: PRISMA flowchart (TikZ)
    ├── hybrid_tls_sequence_tikz.tex  # Fig: TLS handshake (TikZ)
    └── output/                  # Generated figure PDFs go here
        ├── temporal_distribution.pdf
        ├── heatmap_coverage.pdf
        ├── performance_comparison.pdf
        ├── security_level_dist.pdf
        ├── regulatory_timeline.pdf
        ├── radar_chart.pdf
        ├── gap_heatmap.pdf
        └── citation_network.pdf
```

## MRC Scorer Usage

```bash
# Score all six pre-built domain profiles
python mrc_scorer.py --all

# Score a specific domain
python mrc_scorer.py --domain TLS

# JSON output for programmatic use
python mrc_scorer.py --all --json
```

## Overleaf Upload

1. Create a new blank Overleaf project.
2. Upload all files maintaining the directory structure above.
3. Set compiler to `pdflatex`.
4. Upload `IEEEtran.cls` (available at https://www.ieee.org/conferences/publishing/templates.html)
   if not present in your TeX distribution.
5. Compile `pqc_survey_main.tex`.

## Target Venues

| Venue | Impact Factor | Template | Submission |
|-------|--------------|----------|------------|
| IEEE Communications Surveys & Tutorials | 35.6 | IEEEtran (journal) | Primary |
| ACM Computing Surveys | 16.6 | ACM sigconf | Fallback |

## Citation

If using this survey's MRC framework or taxonomy:

```bibtex
@article{[AuthorYear]pqcsurvey,
  author  = {[Authors]},
  title   = {A Comprehensive Survey on Post-Quantum Cryptography Migration},
  journal = {{IEEE} Communications Surveys \& Tutorials},
  year    = {2026},
  note    = {Under review}
}
```
