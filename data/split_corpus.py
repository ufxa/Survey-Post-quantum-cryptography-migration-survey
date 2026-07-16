#!/usr/bin/env python3
"""Split prisma_selection.csv into peer-reviewed, normative, and dedup-log corpora."""
import csv, os

BASE = os.path.dirname(__file__)

NORMATIVE = {
    'NISTIR 8413','NISTIR 8309','NISTIR 8240','NISTIR 8105','Fed. Register',
    'NIST PQC Conf.','NIST Submission','NIST SP 800-208','NIST SP 800-131A',
    'NIST SP 800-175B','NIST Workshop','NIST Conf.','NSA Report','NSA Advisory',
    'ODNI Report','IETF Draft','Blog/WS','Software','RFC 8391','RFC 8554',
    'RFC 8784','OMB Memo','Official Gazette','OJ EU','BSI Report',
    'ENISA Report','ePrint','FIPS 203','FIPS 204','FIPS 205',
}

# key=record_id_padded, value=reason for removal
REMOVE = {
    # NOTE: 019 removed from this dict — it was incorrectly listed as duplicate of itself.
    # 019 (NIST PQC Conf., no DOI) is the CANONICAL pqm4 record; belongs in normative corpus.
    '057': 'Duplicate of 047 (Sikeridis NDSS 2020, DOI 10.14722/ndss.2020.24203)',
    '068': 'Duplicate of 019 (pqm4 Kannwischer, re-entered under IoT subtopic as NIST Conf.)',
    '069': 'Duplicate of 020 (Seo ARM Cortex-M4, DOI 10.1109/ACCESS.2020.3022990)',
    '090': 'Duplicate of 047 (Sikeridis NDSS 2020, re-entered under VPN subtopic)',
    '092': 'Duplicate of 062 (Cooper NIST SP 800-208, DOI 10.6028/NIST.SP.800-208)',
    '093': 'Duplicate of 046 (NSA CNSA 2.0 Advisory, re-entered under VPN subtopic)',
    '101': 'Duplicate of 087 (Busch ESORICS 2021, DOI 10.1007/978-3-030-88418-5_15)',
    '119': 'Duplicate of 035 (Khalid IoT J 2021, DOI 10.1109/JIOT.2020.3033060)',
    '102': 'Duplicate of 065 (Hoffman IEEE S&P Mag 2023, DOI 10.1109/MSEC.2023.3241111)',
}

with open(os.path.join(BASE, 'prisma_selection.csv')) as f:
    reader = csv.DictReader(f)
    fieldnames = list(reader.fieldnames)
    rows = list(reader)

nf = fieldnames + ['corpus_type', 'peer_reviewed', 'audit_note']
peer, norm, dlog = [], [], []

for r in rows:
    rid = r['record_id'].zfill(3)
    r2 = dict(r)
    if rid in REMOVE:
        r2['corpus_type'] = 'REMOVED_DUP'
        r2['peer_reviewed'] = 'N/A'
        r2['audit_note'] = 'DUPLICATE: ' + REMOVE[rid]
        dlog.append(r2)
    elif r['venue'].strip() in NORMATIVE:
        r2['corpus_type'] = 'normative'
        r2['peer_reviewed'] = 'No'
        r2['audit_note'] = 'Grey-lit or normative document; NOT counted in peer-reviewed corpus'
        norm.append(r2)
    else:
        r2['corpus_type'] = 'peer_reviewed'
        r2['peer_reviewed'] = 'Yes'
        r2['audit_note'] = ''
        peer.append(r2)

for fname, data in [
    ('corpus_peer_reviewed.csv', peer),
    ('corpus_normative.csv', norm),
    ('dedup_log.csv', dlog),
]:
    with open(os.path.join(BASE, fname), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=nf)
        w.writeheader()
        w.writerows(data)

print(f'peer_reviewed={len(peer)}, normative={len(norm)}, dups_removed={len(dlog)}')
print(f'Total accounted for: {len(peer)+len(norm)+len(dlog)} (original: {len(rows)})')
