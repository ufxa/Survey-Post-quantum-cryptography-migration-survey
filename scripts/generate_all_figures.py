#!/usr/bin/env python3
"""
PQC Migration Survey -- Figure Generation Suite
Generates all 8 mandatory figures for the IEEE Communications Surveys & Tutorials paper.

Run:  python generate_all_figures.py
Output: PDF files in ./output/ ready for LaTeX inclusion

Dependencies: see ../requirements.txt
  pip install matplotlib seaborn networkx scipy numpy

DATA SOURCES (audit trail):
  - Figs 1, 4: derived from ../data/prisma_selection.csv (72 peer-reviewed records)
  - Fig 3: benchmark values from Kannwischer et al. 2019 (pqm4) and
            Paquin et al. 2020 (OQS-BoringSSL) — see corpus records 017, 039
  - Fig 5: normative document dates from official sources (see pqc_survey.bib)
  - Fig 6: MRC scores produced by ../mrc_scorer.py --all --reference-year 2026
  - Figs 2, 7, 8: qualitative/illustrative — see figure captions for scope
"""

import csv
import os
from collections import Counter, defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import networkx as nx

try:
    import seaborn as sns
    HAS_SNS = True
except ImportError:
    HAS_SNS = False
    print('[WARN] seaborn not available — heatmaps will use matplotlib fallback')

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
CORPUS_CSV = os.path.join(DATA_DIR, 'corpus_peer_reviewed.csv')
PRISMA_CSV = os.path.join(DATA_DIR, 'prisma_selection.csv')

# ─── IEEE Color Palette ───────────────────────────────────────────────────────
C_BLUE   = '#003f87'
C_RED    = '#c0392b'
C_GREEN  = '#1a7a4a'
C_ORANGE = '#e67e22'
C_GRAY   = '#7f8c8d'
C_YELLOW = '#f39c12'
C_PURPLE = '#8e44ad'
C_CYAN   = '#2980b9'

PALETTE  = [C_BLUE, C_RED, C_GREEN, C_ORANGE, C_GRAY, C_YELLOW, C_PURPLE, C_CYAN]

IEEE_FIG  = (3.5, 2.8)
IEEE_WIDE = (7.0, 3.0)

plt.rcParams.update({
    'font.family':       'serif',
    'font.size':         8,
    'axes.titlesize':    9,
    'axes.labelsize':    8,
    'xtick.labelsize':   7,
    'ytick.labelsize':   7,
    'legend.fontsize':   7,
    'figure.dpi':        300,
    'savefig.dpi':       300,
    'savefig.bbox':      'tight',
    'axes.spines.top':   False,
    'axes.spines.right': False,
})


# ─── CSV Loading ─────────────────────────────────────────────────────────────
def load_peer_reviewed_corpus():
    """Load peer-reviewed records from corpus_peer_reviewed.csv.
    Falls back to prisma_selection.csv filtered on included==1 and non-normative venue."""
    if os.path.exists(CORPUS_CSV):
        with open(CORPUS_CSV, newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    # Fallback: read prisma_selection and filter
    rows = []
    if os.path.exists(PRISMA_CSV):
        NORMATIVE_VENUES = {
            'NISTIR 8413','NISTIR 8309','NISTIR 8240','NISTIR 8105','Fed. Register',
            'NIST PQC Conf.','NIST Submission','NIST SP 800-208','NIST SP 800-131A',
            'NIST SP 800-175B','NIST Workshop','NIST Conf.','NSA Report','NSA Advisory',
            'ODNI Report','IETF Draft','Blog/WS','Software','RFC 8391','RFC 8554',
            'RFC 8784','OMB Memo','Official Gazette','OJ EU','BSI Report',
            'ENISA Report','ePrint','FIPS 203','FIPS 204','FIPS 205',
        }
        with open(PRISMA_CSV, newline='', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                if r.get('included', '') == '1' and r.get('venue', '') not in NORMATIVE_VENUES:
                    rows.append(r)
    return rows


CORPUS = load_peer_reviewed_corpus()
print(f'[DATA] Loaded {len(CORPUS)} peer-reviewed records from corpus CSV')


# =============================================================================
# FIG 1 — Temporal Distribution of Publications (2016-2026) by Sub-theme
#          Stacked bar chart — counts from corpus CSV, no synthetic data
# =============================================================================
def fig1_temporal_distribution():
    """Stacked bar chart: publications per year per sub-theme.
    Counts are derived from the peer-reviewed corpus CSV (no synthetic data).
    Error bars are NOT shown because Poisson bootstrapping over
    synthetic counts is methodologically invalid (removed in v2)."""

    # Map CSV subtopic values to display labels
    SUBTOPIC_DISPLAY = {
        'ML-KEM':       'PQC Algorithms',
        'ML-DSA':       'PQC Algorithms',
        'FN-DSA':       'PQC Algorithms',
        'HQC':          'PQC Algorithms',
        'PQC_Algorithms': 'PQC Algorithms',
        'TLS_PKI':      'TLS/PKI',
        'PKI_Cert':     'TLS/PKI',
        'TLS':          'TLS/PKI',
        'IoT_Embedded': 'IoT/Embedded',
        'IoT':          'IoT/Embedded',
        'Blockchain':   'Blockchain',
        'ICS_OT':       'ICS/OT',
        'Regulatory':   'Regulatory',
        'AI_ML_PQC':          'AI/ML + PQC',
        'Crypto_Agility':     'Regulatory',
        'HNDL':               'Regulatory',
        'SLH-DSA_FALCON_HQC': 'PQC Algorithms',
        'FN-DSA':             'PQC Algorithms',
        'SLH-DSA':            'PQC Algorithms',
        'TLS_Hybrid':         'TLS/PKI',
        'VPN_ZeroTrust':      'TLS/PKI',
        'Regulatory_Policy':  'Regulatory',
        'QKD_vs_PQC':         'PQC Algorithms',
        'Hybrid_Schemes':     'PQC Algorithms',
        'Supply_Chain':       'Regulatory',
        'Crypto_Migration':   'TLS/PKI',
    }

    subtopics_ordered = [
        'PQC Algorithms', 'TLS/PKI', 'IoT/Embedded',
        'Blockchain', 'ICS/OT', 'Regulatory', 'AI/ML + PQC',
    ]
    years = list(range(2016, 2027))

    # Accumulate counts from actual corpus
    counts = defaultdict(lambda: defaultdict(int))
    unmapped = Counter()
    for r in CORPUS:
        try:
            yr = int(r.get('year', 0))
        except (ValueError, TypeError):
            continue
        if yr < 2016 or yr > 2026:
            continue
        raw_sub = r.get('subtopic', '').strip()
        display = SUBTOPIC_DISPLAY.get(raw_sub, 'Other')
        if display == 'Other':
            unmapped[raw_sub] += 1
        counts[display][yr] += 1

    if unmapped:
        print(f'[WARN Fig1] Unmapped subtopics (counted as Other): {dict(unmapped)}')

    raw = np.array([
        [counts[st].get(yr, 0) for yr in years]
        for st in subtopics_ordered
    ])

    totals = raw.sum(axis=0)
    total_papers = totals.sum()
    print(f'[Fig1] Corpus total plotted: {total_papers} papers across {years[0]}–{years[-1]}')

    fig, ax = plt.subplots(figsize=IEEE_WIDE)
    x = np.arange(len(years))
    bottom = np.zeros(len(years))

    for i, (topic, color) in enumerate(zip(subtopics_ordered, PALETTE)):
        ax.bar(x, raw[i], bottom=bottom, label=topic, color=color,
               width=0.7, edgecolor='white', linewidth=0.4)
        bottom += raw[i]

    # NIST phase shading (event-based, not year-index-based)
    # Round 1/2: 2016-2019 (indices 0-3), Round 3/4: 2020-2023 (4-7), Post-std: 2024+ (8-)
    ax.axvspan(-0.4, 3.4, alpha=0.06, color='blue', zorder=0)
    ax.axvspan(3.6, 7.4, alpha=0.06, color='green', zorder=0)
    ax.axvspan(7.6, len(years) - 0.4, alpha=0.06, color='orange', zorder=0)

    ymax = max(totals.max(), 5) * 1.25
    ax.text(1.5, ymax * 0.9, 'NIST Round 1/2', fontsize=6, color='blue', ha='center')
    ax.text(5.5, ymax * 0.9, 'Round 3/4', fontsize=6, color='green', ha='center')
    ax.text(9.0, ymax * 0.9, 'Post-Std.', fontsize=6, color='darkorange', ha='center')

    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in years], rotation=35, ha='right')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Publications')
    ax.set_title(
        f'Fig. 1 — Temporal Distribution of PQC Publications (2016–2023)\n'
        f'(n={total_papers}/{len(CORPUS)} papers with year≥2016; 6 seminal pre-2016 works excluded;\n'
        f'2024–2026 corpus coverage incomplete — declared limitation)'
    )
    ax.legend(ncol=4, loc='upper left', framealpha=0.7, fontsize=6)
    ax.set_ylim(0, ymax)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'temporal_distribution.pdf')
    plt.savefig(path)
    plt.close()
    print(f'[OK] Fig 1 saved to {path}')


# =============================================================================
# FIG 2 — Research Coverage Map: Domain vs PQC Algorithm Family
#          NOTE: This is a QUALITATIVE research coverage map based on author
#          analysis of the corpus. Values indicate approximate number of papers
#          addressing each intersection; they are subject to classification
#          uncertainty and should not be interpreted as exact counts.
#          A full cross-tabulation requires manual annotation of all 72 papers.
# =============================================================================
def fig2_heatmap_coverage():
    """Qualitative research coverage map: domain (rows) x algorithm (cols)."""
    domains = ['TLS/Web', 'PKI', 'IoT/Embedded', 'Blockchain', 'VPN/ZTNA', 'ICS/OT']
    algos   = ['ML-KEM\n(Kyber)', 'ML-DSA\n(Dilith.)', 'SLH-DSA\n(SPHINCS+)',
               'FALCON\n(FN-DSA)', 'HQC', 'Hybrid\nSchemes']

    # Qualitative coverage estimates from author corpus analysis.
    # AUDIT NOTE: These are APPROXIMATE counts based on manual paper tagging.
    # Each cell = estimated number of papers addressing the (domain, algorithm) pair.
    # Exact counts require full cross-tabulation annotation of all 72 papers.
    data = np.array([
        [18,  9,  3,  5,  4, 14],   # TLS
        [ 7, 14, 12,  6,  2, 11],   # PKI
        [12,  8,  4, 10,  1,  6],   # IoT
        [ 3,  9,  2,  3,  2,  7],   # Blockchain
        [10,  5,  2,  4,  3,  9],   # VPN
        [ 4,  5,  1,  6,  0,  5],   # ICS/OT
    ])

    fig, ax = plt.subplots(figsize=IEEE_WIDE)

    if HAS_SNS:
        cmap = sns.color_palette('Blues', as_cmap=True)
        sns.heatmap(
            data, annot=True, fmt='d', cmap=cmap,
            linewidths=0.5, linecolor='white',
            xticklabels=algos, yticklabels=domains,
            ax=ax, cbar_kws={'label': 'Approx. papers (qualitative)'},
            annot_kws={'size': 8},
            vmin=0, vmax=20,
        )
    else:
        im = ax.imshow(data, cmap='Blues', vmin=0, vmax=20)
        plt.colorbar(im, ax=ax, label='Approx. papers (qualitative)')
        ax.set_xticks(range(len(algos)))
        ax.set_yticks(range(len(domains)))
        ax.set_xticklabels(algos, fontsize=7)
        ax.set_yticklabels(domains, fontsize=7)
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                ax.text(j, i, str(data[i, j]), ha='center', va='center', fontsize=8)

    # Red for zero cells (research gaps)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if data[i, j] == 0:
                ax.add_patch(plt.Rectangle((j, i), 1, 1, fill=True,
                             color='#c0392b', alpha=0.5, zorder=3))
                ax.text(j + 0.5, i + 0.5, 'GAP',
                        ha='center', va='center', fontsize=7,
                        color='white', fontweight='bold')

    ax.set_title(
        'Fig. 2 — Qualitative Research Coverage: Domain vs. PQC Algorithm\n'
        '(Approx. counts from author corpus analysis; red = zero coverage / gap)'
    )
    ax.set_xlabel('PQC Algorithm Family')
    ax.set_ylabel('Critical Infrastructure Domain')
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'heatmap_coverage.pdf')
    plt.savefig(path)
    plt.close()
    print(f'[OK] Fig 2 saved to {path}')


# =============================================================================
# FIG 3 — Performance Comparison: ML-KEM vs RSA vs ECDH
#          Values from published benchmarks (see DATA SOURCES above)
# =============================================================================
def fig3_performance_comparison():
    """Grouped bar chart: latency (μs) across 3 platforms x 3 algorithms.

    Data sources:
      - Kannwischer et al. 2019 (pqm4): Cortex-M4 values for ML-KEM-768
      - Paquin et al. 2020 (OQS-BoringSSL): server/mobile values
    Error bars represent measurement variance across 1,000 iterations as
    reported in the cited benchmarks.
    """
    platforms  = ['Server\n(x86-64)', 'Mobile\n(ARM A72)', 'IoT\n(Cortex-M4)']
    algorithms = ['ECDH-256', 'RSA-2048', 'ML-KEM-768']
    colors     = [C_BLUE, C_RED, C_GREEN]

    # Latency (microseconds): [keygen, encap/encrypt, decap/decrypt]
    # Sources: pqm4 (Kannwischer 2019, corpus record 017) + OQS-BoringSSL (Paquin 2020, record 039)
    means = {
        'ECDH-256':   [[ 58,  58,  58],  [ 650,  650,  650],  [11278, 11278, 11278]],
        'RSA-2048':   [[ 73, 385, 385],  [1230, 6500, 6500],  [ 6890, 36000, 36000]],
        'ML-KEM-768': [[ 21,  23,  21],  [ 380,  450,  380],  [  886,   963,   863]],
    }
    stds = {
        'ECDH-256':   [[ 2.1,  2.1,  2.1],  [  15,  15,  15],  [ 320, 320, 320]],
        'RSA-2048':   [[ 3.5, 12.0, 12.0],  [  40, 180, 180],  [ 250, 900, 900]],
        'ML-KEM-768': [[ 0.8,  0.9,  0.8],  [  11,  12,  11],  [  28,  31,  29]],
    }
    ops = ['KeyGen', 'Encap/Encry', 'Decap/Decry']

    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.8), sharey=False)
    x = np.arange(len(platforms))
    width = 0.22

    for idx, op in enumerate(ops):
        ax = axes[idx]
        for i, (algo, color) in enumerate(zip(algorithms, colors)):
            m = [means[algo][idx][p] for p in range(len(platforms))]
            s = [stds[algo][idx][p]  for p in range(len(platforms))]
            offset = (i - 1) * width
            ax.bar(x + offset, m, width, label=algo, color=color,
                   yerr=s, capsize=3, error_kw={'linewidth': 1})
        ax.set_xticks(x)
        ax.set_xticklabels(platforms)
        ax.set_title(op, fontsize=8)
        ax.set_ylabel('Latency ($\\mu$s)' if idx == 0 else '')
        ax.set_yscale('log')
        if idx == 0:
            ax.legend(fontsize=6, framealpha=0.7)

    fig.suptitle(
        'Fig. 3 — Performance: ML-KEM-768 vs ECDH-256 vs RSA-2048\n'
        '(log scale; mean $\\pm$ 1 SD from pqm4/OQS-BoringSSL benchmarks)',
        fontsize=8
    )
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'performance_comparison.pdf')
    plt.savefig(path)
    plt.close()
    print(f'[OK] Fig 3 saved to {path}')


# =============================================================================
# FIG 4 — Security Level Distribution by Domain
#          Counts derived from corpus CSV nist_level column
# =============================================================================
def fig4_security_level_dist():
    """Stacked bar: NIST Level 1/3/5 by domain — counts from corpus CSV.
    Pseudo-bootstrap CI removed (was Poisson over synthetic counts; invalid).
    """
    DOMAIN_MAP = {
        'TLS':   'TLS/Web', 'TLS/Web': 'TLS/Web',
        'PKI':   'PKI',     'Gov/PKI': 'PKI',
        'IoT':   'IoT',
        'Blockchain': 'Blockchain',
        'VPN':   'VPN',     'VPN/ZTNA': 'VPN',
        'ICS':   'ICS/OT',  'ICS_OT': 'ICS/OT', 'ICS/OT': 'ICS/OT',
    }
    domains_ordered = ['TLS/Web', 'PKI', 'IoT', 'Blockchain', 'VPN', 'ICS/OT']

    level_counts = defaultdict(lambda: defaultdict(int))
    for r in CORPUS:
        domain_raw = r.get('domain', '').strip()
        domain = DOMAIN_MAP.get(domain_raw, None)
        if domain is None:
            continue
        lvl_raw = r.get('nist_level', '').strip()
        # nist_level field may be "1/3/5", "1", "3", "5", "1/3", etc.
        for lvl in lvl_raw.split('/'):
            try:
                lvl_int = int(lvl.strip())
                if lvl_int in (1, 3, 5):
                    level_counts[domain][lvl_int] += 1
            except ValueError:
                pass

    level1 = np.array([level_counts[d][1] for d in domains_ordered])
    level3 = np.array([level_counts[d][3] for d in domains_ordered])
    level5 = np.array([level_counts[d][5] for d in domains_ordered])
    totals = level1 + level3 + level5

    total_classified = totals.sum()
    print(f'[Fig4] Domain-classified papers: {total_classified} '
          f'(papers with domain="All" or unmapped are excluded from this figure)')

    x = np.arange(len(domains_ordered))
    fig, ax = plt.subplots(figsize=IEEE_WIDE)
    w = 0.55
    ax.bar(x, level1, w, label='NIST Level 1 (~AES-128)', color=C_GREEN)
    ax.bar(x, level3, w, bottom=level1, label='NIST Level 3 (~AES-192)', color=C_BLUE)
    ax.bar(x, level5, w, bottom=level1 + level3, label='NIST Level 5 (~AES-256)', color=C_RED)

    ax.set_xticks(x)
    ax.set_xticklabels(domains_ordered)
    ax.set_xlabel('Domain')
    ax.set_ylabel('Number of Papers')
    ax.set_title(
        f'Fig. 4 — NIST Security Level Distribution by Domain\n'
        f'(n={total_classified} domain-classified papers; source: corpus CSV)'
    )
    ax.legend(loc='upper right', fontsize=7)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'security_level_dist.pdf')
    plt.savefig(path)
    plt.close()
    print(f'[OK] Fig 4 saved to {path}')


# =============================================================================
# FIG 5 — Regulatory Deadline Timeline (Gantt-style)
#          Dates from official normative documents (see pqc_survey.bib)
# =============================================================================
def fig5_regulatory_timeline():
    """Gantt-style regulatory deadline chart.
    All dates are from official normative sources cited in pqc_survey.bib."""
    tasks = [
        # (framework, sector, start_year, end_year, color)
        ('NIST SP 800-208',       'Gov. Signing',   2020, 2025, C_BLUE),
        ('OMB M-23-02',           'Federal IT',     2022, 2025, C_BLUE),
        ('NSA CNSA 2.0 (SW)',     'NSS Software',   2022, 2025, C_RED),
        ('NSA CNSA 2.0 (Prod)',   'NSS Products',   2022, 2026, C_RED),
        ('NSA CNSA 2.0 (Legacy)', 'NSS Legacy',     2022, 2033, C_RED),
        ('ENISA Rec.',            'EU CIP',         2021, 2030, C_GREEN),
        ('BSI/ANSSI',             'EU Gov.',        2021, 2030, C_GREEN),
        ('ETSI QSC',              'Telecom',        2020, 2028, C_ORANGE),
        ('LGPD (Implicit)',       'BR Data Ctrl.',  2023, 2028, C_GRAY),
        ('3GPP 5G SA3',           '5G Networks',    2023, 2027, C_PURPLE),
        ('FIPS 203/204/205',      'All US Fed.',    2024, 2033, C_CYAN),
        ('EO 14412',              'US Federal',     2026, 2033, C_RED),
        ('OMB M-26-15',           'US Agencies',    2026, 2033, C_BLUE),
    ]

    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    for idx, (fw, sector, s, e, color) in enumerate(tasks):
        ax.barh(idx, e - s, left=s, height=0.55, color=color, alpha=0.8, edgecolor='white')
        ax.text(s + 0.1, idx, fw, va='center', ha='left', fontsize=6.5,
                color='white', fontweight='bold')
        ax.text(e + 0.05, idx, str(e), va='center', ha='left', fontsize=6, color=color)

    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels([f'{fw} / {sector}' for fw, sector, *_ in tasks], fontsize=6.5)
    ax.set_xlim(2019, 2035)
    ax.set_xlabel('Year')
    ax.set_title(
        'Fig. 5 — Regulatory PQC Migration Deadline Timeline\n'
        '(Gantt-style; dates from official normative sources)'
    )
    ax.axvline(2026, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
    ax.text(2026.1, len(tasks) - 0.5, 'Today (2026)', fontsize=6.5,
            color='black', alpha=0.7)
    ax.grid(axis='x', linestyle=':', alpha=0.4)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'regulatory_timeline.pdf')
    plt.savefig(path)
    plt.close()
    print(f'[OK] Fig 5 saved to {path}')


# =============================================================================
# FIG 6 — MRC Migration Readiness Radar Chart
#          Values from mrc_scorer.py --all --reference-year 2026
# =============================================================================
def fig6_radar_chart():
    """Spider/radar chart: MRC dimension scores per domain.

    All values generated by running: python ../mrc_scorer.py --all --json --reference-year 2026
    DO NOT edit these values manually — run the scorer and update from its JSON output.

    Output (reference-year=2026):
      TLS/Web:    E=0.6000  1-F=0.6667  1-D=1.0000  MRC=0.7033  T2
      PKI:        E=0.8333  1-F=0.6667  1-D=0.9000  MRC=0.7883  T1
      IoT:        E=0.6000  1-F=0.5000  1-D=0.8000  MRC=0.6050  T2
      ICS/OT:     E=0.7500  1-F=0.5000  1-D=0.5000  MRC=0.6125  T2
      Blockchain: E=0.6000  1-F=0.6000  1-D=0.8000  MRC=0.6400  T2
      VPN/ZTNA:   E=0.7500  1-F=1.0000  1-D=1.0000  MRC=0.8875  T1
    """
    domains = ['TLS/Web', 'PKI', 'IoT', 'ICS/OT', 'Blockchain', 'VPN/ZTNA']
    dims    = ['Exposure\n(E)', 'Upgrade\nFeasibility\n(1-F)', 'Deadline\nProximity\n(1-D)', 'MRC\nScore']

    # [E, 1-F, 1-D, MRC] — from mrc_scorer.py --all --reference-year 2026
    data = {
        'TLS/Web':   [0.6000, 0.6667, 1.0000, 0.7033],
        'PKI':       [0.8333, 0.6667, 0.9000, 0.7883],
        'IoT':       [0.6000, 0.5000, 0.8000, 0.6050],
        'ICS/OT':    [0.7500, 0.5000, 0.5000, 0.6125],
        'Blockchain':[0.6000, 0.6000, 0.8000, 0.6400],
        'VPN/ZTNA':  [0.7500, 1.0000, 1.0000, 0.8875],
    }

    N = len(dims)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(3.5, 3.5), subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dims, fontsize=6.5)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.50, 0.75, 1.0])
    ax.set_yticklabels(['0.25', '0.50', '0.75', '1.00'], fontsize=5.5)

    # Tier thresholds
    ax.axhline(0.75, color=C_RED,    linestyle='--', linewidth=0.7, alpha=0.5)
    ax.axhline(0.50, color=C_ORANGE, linestyle='--', linewidth=0.7, alpha=0.5)

    tier_colors = {
        'TLS/Web':   C_ORANGE,  # T2
        'PKI':       C_RED,     # T1
        'IoT':       C_ORANGE,  # T2
        'ICS/OT':    C_ORANGE,  # T2
        'Blockchain':C_ORANGE,  # T2
        'VPN/ZTNA':  C_RED,     # T1
    }

    for domain, vals in data.items():
        v = vals + vals[:1]
        ax.plot(angles, v, linewidth=1.2, color=tier_colors[domain], label=domain)
        ax.fill(angles, v, alpha=0.05, color=tier_colors[domain])

    ax.set_title(
        'Fig. 6 — MRC Migration Readiness Radar\n(mrc_scorer.py, ref-year=2026)',
        fontsize=8, pad=20
    )
    ax.legend(loc='upper right', bbox_to_anchor=(1.55, 1.15), fontsize=6)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'radar_chart.pdf')
    plt.savefig(path)
    plt.close()
    print(f'[OK] Fig 6 saved to {path}')


# =============================================================================
# FIG 7 — Research Gap Heatmap
#          QUALITATIVE expert assessment — NOT paper counts
# =============================================================================
def fig7_gap_heatmap():
    """Qualitative gap severity heatmap: problem dimension x solution approach.

    AUDIT NOTE: Cell values represent the authors' qualitative assessment of
    research coverage intensity (0=no coverage, 5=strong coverage), NOT exact
    paper counts. A full bibliometric cross-tabulation would require complete
    manual annotation of all 72 papers by both dimensions simultaneously.
    This figure is intended to identify research directions, not to report
    precise counts.
    """
    problems = [
        'Ultra-constrained devices (<64 KB)',
        'Automated crypto inventory',
        'Safety-security co-design (ICS)',
        'Crypto-agility metrics',
        'Economic migration models',
        'PQC interoperability testing',
        'Hybrid scheme standardization',
        'Regulatory cross-mapping',
        'Long-lived data protection',
        'Supply chain PQC assurance',
    ]
    gap_labels = ['G1', 'G2', 'G3', 'G4', 'G5', 'G6']
    solutions = [
        'Lightweight\nalgorithms',
        'Static\nanalysis',
        'Formal\nmethods',
        'HW accel-\neration',
        'Policy &\nstandards',
        'Performance\nbenchmarks',
        'Economic\nmodeling',
        'Interop\ntesting',
    ]

    # Qualitative coverage intensity (0=none, 5=high) — author assessment
    data = np.array([
        [1, 0, 0, 4, 0, 3, 0, 0],  # G1: ultra-constrained
        [0, 2, 0, 0, 1, 0, 0, 0],  # G2: crypto inventory
        [0, 0, 1, 0, 0, 0, 0, 0],  # G3: safety-security
        [0, 1, 2, 0, 2, 1, 0, 0],  # G4: crypto-agility
        [0, 0, 0, 0, 1, 0, 1, 0],  # G5: economic models
        [0, 0, 0, 0, 1, 3, 0, 2],  # G6: interoperability
        [3, 0, 0, 0, 5, 0, 0, 2],  # hybrid standardization
        [0, 0, 0, 0, 4, 0, 0, 0],  # regulatory
        [2, 0, 0, 0, 2, 0, 1, 0],  # long-lived data
        [0, 1, 1, 0, 3, 0, 0, 1],  # supply chain
    ])

    fig, ax = plt.subplots(figsize=IEEE_WIDE)

    if HAS_SNS:
        cmap = sns.light_palette(C_BLUE, as_cmap=True)
        sns.heatmap(data, annot=True, fmt='d', cmap=cmap,
                    xticklabels=solutions, yticklabels=problems,
                    linewidths=0.4, linecolor='white',
                    ax=ax,
                    cbar_kws={'label': 'Coverage intensity (qualitative, 0–5)'},
                    annot_kws={'size': 8})
    else:
        im = ax.imshow(data, cmap='Blues', vmin=0, vmax=5)
        plt.colorbar(im, ax=ax, label='Coverage intensity (qualitative, 0–5)')
        ax.set_xticks(range(len(solutions)))
        ax.set_yticks(range(len(problems)))
        ax.set_xticklabels(solutions, fontsize=7)
        ax.set_yticklabels(problems, fontsize=7)
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                ax.text(j, i, str(data[i, j]), ha='center', va='center', fontsize=8)

    # Red overlay for gaps in G1-G6
    for i in range(6):
        for j in range(data.shape[1]):
            if data[i, j] == 0:
                ax.add_patch(plt.Rectangle((j, i), 1, 1, fill=True,
                             color='#c0392b', alpha=0.35, zorder=3))

    # G1-G6 labels on the right side (outside heatmap, before colorbar)
    n_cols = data.shape[1]
    for i, lbl in enumerate(gap_labels):
        ax.text(n_cols + 0.15, i + 0.5, lbl,
                ha='left', va='center', fontsize=8,
                color='#c0392b', fontweight='bold',
                transform=ax.transData)

    ax.set_title(
        'Fig. 7 — Research Gap Heatmap\n'
        '(Red = zero coverage; G1--G6 annotate critical gaps)'
    )
    ax.set_xlabel('Solution Approach')
    ax.set_ylabel('Problem Dimension')
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'gap_heatmap.pdf')
    plt.savefig(path)
    plt.close()
    print(f'[OK] Fig 7 saved to {path}')


# =============================================================================
# FIG 8 — Illustrative Co-Citation Map of Key Papers
#          NOTE: Edge topology is based on author analysis of thematic
#          relationships in the corpus. This is not a computationally derived
#          citation network; it illustrates conceptual lineage.
# =============================================================================
def fig8_citation_network():
    """Illustrative co-citation map of key papers in the corpus.

    AUDIT NOTE: Node selection (20 most-cited/foundational) and edge topology
    are based on the authors' analysis of thematic relationships and explicit
    cross-references identified in the screened corpus. This is NOT a
    computationally derived citation graph from a database (e.g., WoS, Scopus).
    It should be read as a conceptual lineage map, not a bibliometric network.
    """
    G = nx.DiGraph()
    nodes = [
        ('NIST FIPS 203', 'Standard'),
        ('NIST FIPS 204', 'Standard'),
        ('NIST FIPS 205', 'Standard'),
        ('Shor 1994',     'Seminal'),
        ('Grover 1996',   'Seminal'),
        ('Bernstein 2017','Survey'),
        ('Joseph 2022',   'Survey'),
        ('Bos 2018',      'Algorithm'),
        ('Ducas 2018',    'Algorithm'),
        ('Bernstein 2019','Algorithm'),
        ('Prest 2022',    'Algorithm'),
        ('Mosca 2018',    'Threat Model'),
        ('Stebila 2020',  'Protocol'),
        ('Paquin 2020',   'Protocol'),
        ('Kannwischer 2019','Benchmark'),
        ('Nejatollahi 2019','Survey'),
        ('Fernandez 2020','Domain'),
        ('Liu 2021',      'Domain'),
        ('Sikeridis 2020','Protocol'),
    ]

    color_map = {
        'Standard':    C_RED,
        'Seminal':     C_GRAY,
        'Survey':      C_BLUE,
        'Algorithm':   C_GREEN,
        'Threat Model':C_ORANGE,
        'Protocol':    C_CYAN,
        'Benchmark':   C_YELLOW,
        'Domain':      C_PURPLE,
    }

    for name, category in nodes:
        G.add_node(name, category=category)

    edges = [
        ('NIST FIPS 203', 'Bos 2018'),
        ('NIST FIPS 204', 'Ducas 2018'),
        ('NIST FIPS 205', 'Bernstein 2019'),
        ('Shor 1994',     'NIST FIPS 203'),
        ('Shor 1994',     'NIST FIPS 204'),
        ('Shor 1994',     'Mosca 2018'),
        ('Grover 1996',   'Mosca 2018'),
        ('Grover 1996',   'NIST FIPS 203'),
        ('Bos 2018',      'Stebila 2020'),
        ('Bos 2018',      'Paquin 2020'),
        ('Bos 2018',      'Kannwischer 2019'),
        ('Ducas 2018',    'Kannwischer 2019'),
        ('Bernstein 2019','Kannwischer 2019'),
        ('Mosca 2018',    'Joseph 2022'),
        ('Mosca 2018',    'Stebila 2020'),
        ('Bernstein 2017','Joseph 2022'),
        ('Bernstein 2017','Nejatollahi 2019'),
        ('Nejatollahi 2019','Kannwischer 2019'),
        ('Nejatollahi 2019','Liu 2021'),
        ('Stebila 2020',  'Sikeridis 2020'),
        ('Paquin 2020',   'Sikeridis 2020'),
        ('Prest 2022',    'NIST FIPS 205'),
        ('Liu 2021',      'Fernandez 2020'),
    ]

    for src, dst in edges:
        if src in G and dst in G:
            G.add_edge(src, dst)

    np.random.seed(42)
    pos = nx.spring_layout(G, seed=42, k=2.5)
    node_colors = [color_map[G.nodes[n]['category']] for n in G.nodes]
    node_sizes  = [400 + 60 * G.in_degree(n) for n in G.nodes]

    fig, ax = plt.subplots(figsize=IEEE_WIDE)
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes,
                           alpha=0.88, ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color=C_GRAY, alpha=0.5,
                           arrows=True, arrowsize=12, ax=ax,
                           connectionstyle='arc3,rad=0.1')
    nx.draw_networkx_labels(G, pos, font_size=5.5, ax=ax)

    legend_elements = [mpatches.Patch(facecolor=color_map[cat], label=cat)
                       for cat in color_map]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=6,
              framealpha=0.8, ncol=2)
    ax.set_title(
        'Fig. 8 — Illustrative Co-Citation Map of Key Papers\n'
        '(Author-curated thematic lineage; NOT a computed bibliometric graph)'
    )
    ax.axis('off')
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, 'citation_network.pdf')
    plt.savefig(path)
    plt.close()
    print(f'[OK] Fig 8 saved to {path}')


# =============================================================================
# Main
# =============================================================================
if __name__ == '__main__':
    print('Generating all 8 figures for PQC Migration Survey...\n')
    fig1_temporal_distribution()
    fig2_heatmap_coverage()
    fig3_performance_comparison()
    fig4_security_level_dist()
    fig5_regulatory_timeline()
    fig6_radar_chart()
    fig7_gap_heatmap()
    fig8_citation_network()
    print(f'\nAll figures written to: {OUTPUT_DIR}/')
    print('NOTE: Run mrc_scorer.py --all --json --reference-year 2026 to verify Fig 6 inputs.')
