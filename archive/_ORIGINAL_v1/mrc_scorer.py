#!/usr/bin/env python3
"""
MRC (Migration Readiness Classification) Framework
Implementation of Algorithm 1 from the PQC Migration Survey.

Usage:
    python mrc_scorer.py --domain TLS
    python mrc_scorer.py --interactive
    python mrc_scorer.py --batch data/mrc_inputs.csv

Reference:
    "A Comprehensive Survey on Post-Quantum Cryptography Migration"
    IEEE Communications Surveys & Tutorials, 2026
"""

import argparse
import csv
import json
import sys
from dataclasses import dataclass, field, asdict
from typing import List, Optional


# ─── Weights (Analytic Hierarchy Process, Saaty CR = 0.04) ──────────────────
W_EXPOSURE    = 0.45   # Cryptographic exposure
W_FEASIBILITY = 0.35   # Upgrade feasibility (inverse: 1 - F)
W_DEADLINE    = 0.20   # Regulatory deadline proximity (inverse: 1 - D)

DEADLINE_WINDOW_YEARS = 10  # Normalization window for deadline score


# ─── Data Structures ─────────────────────────────────────────────────────────
@dataclass
class CryptographicAsset:
    """Represents a single cryptographic function/component."""
    name: str
    algorithm: str
    quantum_vulnerable: bool
    domain: str
    notes: str = ''


@dataclass
class UpgradeConstraint:
    """Represents an upgrade pathway constraint."""
    component: str
    requires_hardware_replacement: bool
    estimated_cost_usd: Optional[float] = None
    upgrade_timeline_months: Optional[int] = None


@dataclass
class RegulatoryContext:
    """Maps regulatory obligations to deadlines."""
    frameworks: List[dict] = field(default_factory=list)

    def get_earliest_deadline(self, reference_year: int = 2026) -> int:
        if not self.frameworks:
            return reference_year + 10  # default: 10 years
        return min(fw.get('deadline_year', reference_year + 10)
                   for fw in self.frameworks)


@dataclass
class SystemProfile:
    """Full profile of a system under MRC assessment."""
    name: str
    domain: str
    crypto_assets: List[CryptographicAsset] = field(default_factory=list)
    upgrade_constraints: List[UpgradeConstraint] = field(default_factory=list)
    regulatory_context: Optional[RegulatoryContext] = None
    reference_year: int = 2026


@dataclass
class MRCResult:
    """Output of the MRC scoring algorithm."""
    system_name: str
    domain: str
    exposure_score: float
    feasibility_score: float
    deadline_score: float
    mrc_score: float
    tier: str
    tier_label: str
    recommended_action: str
    details: dict = field(default_factory=dict)


# ─── MRC Algorithm ───────────────────────────────────────────────────────────
TIER_DEFINITIONS = [
    (0.75, 'T1', 'Critical',
     'Immediate hybrid migration; emergency budget allocation required.'),
    (0.50, 'T2', 'High',
     'Begin migration planning; procure PQC-enabled hardware.'),
    (0.25, 'T3', 'Medium',
     'Monitor standards; update crypto-agility frameworks.'),
    (0.00, 'T4', 'Low',
     'Inventory cryptographic assets; schedule review by 2028.'),
]

QUANTUM_VULNERABLE_ALGORITHMS = {
    'rsa', 'ecdh', 'ecdsa', 'dh', 'dsa', 'elgamal',
    'rsa-2048', 'rsa-4096', 'ecdh-256', 'ecdsa-256',
    'p-256', 'p-384', 'x25519', 'ed25519',
}


def is_quantum_vulnerable(algorithm: str) -> bool:
    """Return True if the algorithm is broken by Shor's algorithm."""
    return algorithm.lower().strip() in QUANTUM_VULNERABLE_ALGORITHMS


def compute_exposure_score(assets: List[CryptographicAsset]) -> float:
    """E = fraction of crypto functions using quantum-vulnerable primitives."""
    if not assets:
        return 0.0
    vulnerable = sum(1 for a in assets if a.quantum_vulnerable)
    return vulnerable / len(assets)


def compute_feasibility_score(constraints: List[UpgradeConstraint]) -> float:
    """F = fraction of components requiring hardware replacement (0=easy, 1=hard)."""
    if not constraints:
        return 0.0
    hw_replace = sum(1 for c in constraints if c.requires_hardware_replacement)
    return hw_replace / len(constraints)


def compute_deadline_score(regulatory: Optional[RegulatoryContext],
                            reference_year: int) -> float:
    """D = normalized deadline proximity [0,1]. Higher = more time remaining."""
    if regulatory is None:
        return 0.5  # default: moderate urgency
    earliest = regulatory.get_earliest_deadline(reference_year)
    years_remaining = earliest - reference_year
    return min(1.0, max(0.0, years_remaining / DEADLINE_WINDOW_YEARS))


def classify_tier(score: float) -> tuple:
    """Return (tier_id, tier_label, recommended_action) for a given MRC score."""
    for threshold, tier_id, label, action in TIER_DEFINITIONS:
        if score >= threshold:
            return tier_id, label, action
    return 'T4', 'Low', TIER_DEFINITIONS[-1][3]


def score_system(profile: SystemProfile) -> MRCResult:
    """
    Main MRC scoring function implementing Algorithm 1.

    MRC(S) = 0.45 * E + 0.35 * (1 - F) + 0.20 * (1 - D)
    """
    E = compute_exposure_score(profile.crypto_assets)
    F = compute_feasibility_score(profile.upgrade_constraints)
    D = compute_deadline_score(profile.regulatory_context, profile.reference_year)

    mrc_score = W_EXPOSURE * E + W_FEASIBILITY * (1 - F) + W_DEADLINE * (1 - D)
    mrc_score = round(min(1.0, max(0.0, mrc_score)), 4)

    tier_id, tier_label, action = classify_tier(mrc_score)

    return MRCResult(
        system_name=profile.name,
        domain=profile.domain,
        exposure_score=round(E, 4),
        feasibility_score=round(F, 4),
        deadline_score=round(D, 4),
        mrc_score=mrc_score,
        tier=tier_id,
        tier_label=tier_label,
        recommended_action=action,
        details={
            'n_assets': len(profile.crypto_assets),
            'n_vulnerable': sum(1 for a in profile.crypto_assets if a.quantum_vulnerable),
            'n_constraints': len(profile.upgrade_constraints),
            'n_hw_replace': sum(1 for c in profile.upgrade_constraints
                                if c.requires_hardware_replacement),
            'weight_E': W_EXPOSURE,
            'weight_F': W_FEASIBILITY,
            'weight_D': W_DEADLINE,
            'formula': f'{W_EXPOSURE}*E + {W_FEASIBILITY}*(1-F) + {W_DEADLINE}*(1-D)',
            'substituted': f'{W_EXPOSURE}*{E:.3f} + {W_FEASIBILITY}*(1-{F:.3f}) + {W_DEADLINE}*(1-{D:.3f})',
        }
    )


# ─── Pre-built Domain Profiles (from survey Section VI) ──────────────────────
def build_domain_profiles() -> List[SystemProfile]:
    """Return reference system profiles for the six critical domains."""

    tls_profile = SystemProfile(
        name='Enterprise TLS/HTTPS Infrastructure',
        domain='TLS/Web',
        crypto_assets=[
            CryptographicAsset('TLS Key Exchange', 'ECDH', True, 'TLS'),
            CryptographicAsset('TLS Auth Sig', 'ECDSA', True, 'TLS'),
            CryptographicAsset('Server Cert', 'RSA-2048', True, 'TLS'),
            CryptographicAsset('HMAC-SHA256', 'SHA-256', False, 'TLS'),
            CryptographicAsset('AES-256-GCM', 'AES-256', False, 'TLS'),
        ],
        upgrade_constraints=[
            UpgradeConstraint('Web Server (OpenSSL)', requires_hardware_replacement=False,
                               upgrade_timeline_months=3),
            UpgradeConstraint('Load Balancer (F5)', requires_hardware_replacement=False,
                               upgrade_timeline_months=6),
            UpgradeConstraint('HSM (Luna)', requires_hardware_replacement=True,
                               estimated_cost_usd=80_000, upgrade_timeline_months=12),
        ],
        regulatory_context=RegulatoryContext(frameworks=[
            {'name': 'NIST FIPS 203', 'deadline_year': 2027},
            {'name': 'OMB M-23-02',   'deadline_year': 2025},
        ]),
    )

    pki_profile = SystemProfile(
        name='Enterprise PKI / CA Infrastructure',
        domain='PKI',
        crypto_assets=[
            CryptographicAsset('Root CA Signature', 'RSA-4096', True, 'PKI'),
            CryptographicAsset('Intermediate CA Sig', 'RSA-2048', True, 'PKI'),
            CryptographicAsset('End-Entity Cert', 'ECDSA-256', True, 'PKI'),
            CryptographicAsset('OCSP Signature', 'RSA-2048', True, 'PKI'),
            CryptographicAsset('CRL Signature', 'RSA-2048', True, 'PKI'),
            CryptographicAsset('SHA-256 Hash', 'SHA-256', False, 'PKI'),
        ],
        upgrade_constraints=[
            UpgradeConstraint('Root CA HSM', requires_hardware_replacement=True,
                               estimated_cost_usd=200_000, upgrade_timeline_months=18),
            UpgradeConstraint('Sub CA Software', requires_hardware_replacement=False,
                               upgrade_timeline_months=6),
            UpgradeConstraint('Certificate Templates', requires_hardware_replacement=False,
                               upgrade_timeline_months=3),
        ],
        regulatory_context=RegulatoryContext(frameworks=[
            {'name': 'NIST FIPS 204', 'deadline_year': 2027},
        ]),
    )

    iot_profile = SystemProfile(
        name='IoT Fleet (Class 1 Devices)',
        domain='IoT',
        crypto_assets=[
            CryptographicAsset('Device Auth', 'ECDSA-256', True, 'IoT'),
            CryptographicAsset('Key Exchange', 'ECDH', True, 'IoT'),
            CryptographicAsset('Firmware Sig', 'RSA-2048', True, 'IoT'),
            CryptographicAsset('Session Encryption', 'AES-128', False, 'IoT'),
            CryptographicAsset('HMAC-SHA256', 'SHA-256', False, 'IoT'),
        ],
        upgrade_constraints=[
            UpgradeConstraint('Firmware OTA', requires_hardware_replacement=False,
                               upgrade_timeline_months=6),
            UpgradeConstraint('Crypto Co-Processor', requires_hardware_replacement=True,
                               upgrade_timeline_months=36),
            UpgradeConstraint('Secure Element', requires_hardware_replacement=True,
                               upgrade_timeline_months=24),
            UpgradeConstraint('TLS Library', requires_hardware_replacement=False,
                               upgrade_timeline_months=4),
        ],
        regulatory_context=RegulatoryContext(frameworks=[
            {'name': 'ETSI EN 303 645', 'deadline_year': 2028},
        ]),
    )

    ics_profile = SystemProfile(
        name='Industrial Control System (SCADA)',
        domain='ICS/OT',
        crypto_assets=[
            CryptographicAsset('SCADA Auth', 'RSA-2048', True, 'ICS'),
            CryptographicAsset('PLC Firmware', 'ECDSA', True, 'ICS'),
            CryptographicAsset('Historian DB', 'AES-256', False, 'ICS'),
            CryptographicAsset('OPC-UA TLS', 'ECDH', True, 'ICS'),
        ],
        upgrade_constraints=[
            UpgradeConstraint('PLCs (Siemens S7)', requires_hardware_replacement=True,
                               estimated_cost_usd=500_000, upgrade_timeline_months=60),
            UpgradeConstraint('RTUs (ABB)', requires_hardware_replacement=True,
                               estimated_cost_usd=300_000, upgrade_timeline_months=48),
            UpgradeConstraint('SCADA Server', requires_hardware_replacement=False,
                               upgrade_timeline_months=12),
            UpgradeConstraint('Historian', requires_hardware_replacement=False,
                               upgrade_timeline_months=6),
        ],
        regulatory_context=RegulatoryContext(frameworks=[
            {'name': 'IEC 62443', 'deadline_year': 2031},
            {'name': 'NIST CSF',  'deadline_year': 2033},
        ]),
    )

    blockchain_profile = SystemProfile(
        name='Enterprise Blockchain / DLT',
        domain='Blockchain',
        crypto_assets=[
            CryptographicAsset('Wallet Keys', 'ECDSA-256', True, 'Blockchain'),
            CryptographicAsset('Consensus Sig', 'ECDSA', True, 'Blockchain'),
            CryptographicAsset('ZKP (SNARK)', 'ECDH', True, 'Blockchain'),
            CryptographicAsset('SHA-256 Hash', 'SHA-256', False, 'Blockchain'),
            CryptographicAsset('AES-256', 'AES-256', False, 'Blockchain'),
        ],
        upgrade_constraints=[
            UpgradeConstraint('Protocol Hard Fork', requires_hardware_replacement=False,
                               upgrade_timeline_months=24),
            UpgradeConstraint('Wallet Migration', requires_hardware_replacement=False,
                               upgrade_timeline_months=12),
            UpgradeConstraint('Smart Contracts', requires_hardware_replacement=False,
                               upgrade_timeline_months=18),
            UpgradeConstraint('Consensus Nodes', requires_hardware_replacement=True,
                               upgrade_timeline_months=6),
            UpgradeConstraint('Hardware Wallets', requires_hardware_replacement=True,
                               upgrade_timeline_months=18),
        ],
        regulatory_context=RegulatoryContext(frameworks=[
            {'name': 'MiCA (EU)', 'deadline_year': 2028},
        ]),
    )

    vpn_profile = SystemProfile(
        name='Enterprise VPN / ZTNA',
        domain='VPN/ZTNA',
        crypto_assets=[
            CryptographicAsset('IKEv2 DH', 'ECDH', True, 'VPN'),
            CryptographicAsset('IPSec Auth', 'ECDSA', True, 'VPN'),
            CryptographicAsset('TLS Auth', 'RSA-2048', True, 'VPN'),
            CryptographicAsset('AES-256-GCM', 'AES-256', False, 'VPN'),
        ],
        upgrade_constraints=[
            UpgradeConstraint('VPN Gateway (Cisco)', requires_hardware_replacement=False,
                               upgrade_timeline_months=6),
            UpgradeConstraint('Certificate (PKI)', requires_hardware_replacement=False,
                               upgrade_timeline_months=3),
            UpgradeConstraint('Client Software', requires_hardware_replacement=False,
                               upgrade_timeline_months=4),
        ],
        regulatory_context=RegulatoryContext(frameworks=[
            {'name': 'NSA CNSA 2.0', 'deadline_year': 2026},
        ]),
    )

    return [tls_profile, pki_profile, iot_profile, ics_profile, blockchain_profile, vpn_profile]


# ─── CLI ─────────────────────────────────────────────────────────────────────
def print_result(r: MRCResult):
    print(f'\n{"="*60}')
    print(f'  System: {r.system_name}')
    print(f'  Domain: {r.domain}')
    print(f'{"─"*60}')
    print(f'  Exposure Score (E):        {r.exposure_score:.4f}')
    print(f'  Feasibility Score (1-F):   {1 - r.feasibility_score:.4f}')
    print(f'  Deadline Score (1-D):      {1 - r.deadline_score:.4f}')
    print(f'  ──────────────────────────────────────')
    print(f'  MRC Score:                 {r.mrc_score:.4f}')
    print(f'  Tier:                      {r.tier} ({r.tier_label})')
    print(f'  Action:                    {r.recommended_action}')
    print(f'{"="*60}')


def main():
    parser = argparse.ArgumentParser(
        description='MRC Migration Readiness Classification Scorer')
    parser.add_argument('--domain', choices=['TLS', 'PKI', 'IoT', 'ICS', 'Blockchain', 'VPN'],
                        help='Score a pre-built domain profile')
    parser.add_argument('--all', action='store_true',
                        help='Score all six pre-built domain profiles')
    parser.add_argument('--json', action='store_true',
                        help='Output results as JSON')
    args = parser.parse_args()

    profiles = build_domain_profiles()

    if args.all or not args.domain:
        results = [score_system(p) for p in profiles]
        if args.json:
            print(json.dumps([asdict(r) for r in results], indent=2))
        else:
            for r in results:
                print_result(r)
        return

    domain_map = {
        'TLS': profiles[0],
        'PKI': profiles[1],
        'IoT': profiles[2],
        'ICS': profiles[3],
        'Blockchain': profiles[4],
        'VPN': profiles[5],
    }
    profile = domain_map.get(args.domain)
    if profile:
        result = score_system(profile)
        if args.json:
            print(json.dumps(asdict(result), indent=2))
        else:
            print_result(result)


if __name__ == '__main__':
    main()
