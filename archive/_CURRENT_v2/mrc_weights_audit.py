#!/usr/bin/env python3
"""
AHP Weight Audit for MRC Framework
Demonstrates that the AHP matrix published in the companion paper produces
w=[0.633, 0.261, 0.106] with CR=0.033, NOT the claimed 0.45/0.35/0.20.

Saaty's AHP procedure (3-criterion case):
  1. Build pairwise comparison matrix A
  2. Normalize each column by its sum
  3. Weights = row means of normalized matrix
  4. Compute lambda_max and CR to validate consistency

Reference: Saaty, T.L. (1980). The Analytic Hierarchy Process. McGraw-Hill.
"""

import math


def ahp_3x3(a12, a13, a23):
    """
    Compute AHP weights and CR for a 3x3 matrix given the upper-triangle entries.
    a_ij means "criterion i is a_ij times more important than criterion j".
    Lower triangle = 1/a_ij (reciprocal).

    Returns: weights (list[float]), lambda_max (float), CI (float), CR (float)
    """
    A = [
        [1,      a12,     a13],
        [1/a12,  1,       a23],
        [1/a13,  1/a23,   1  ],
    ]

    col_sums = [sum(A[r][c] for r in range(3)) for c in range(3)]
    norm = [[A[r][c] / col_sums[c] for c in range(3)] for r in range(3)]
    weights = [sum(norm[r]) / 3 for r in range(3)]

    # Weighted sum vector
    ws = [sum(A[r][c] * weights[c] for c in range(3)) for r in range(3)]
    lambdas = [ws[r] / weights[r] for r in range(3)]
    lambda_max = sum(lambdas) / 3

    CI = (lambda_max - 3) / (3 - 1)
    RI = 0.58  # Saaty's random index for n=3
    CR = CI / RI

    return weights, lambda_max, CI, CR


def main():
    print("=" * 62)
    print("  AHP Weight Audit — MRC Framework")
    print("=" * 62)
    print()

    # ── Matrix from companion paper (Section VI) ──────────────────
    # The paper states: "E is 3x more important than F, 5x more than D;
    # F is 3x more important than D." (paraphrase — see Table VI in paper)
    # These are the a_ij values implied by the narrative.
    A12_paper = 3    # E vs F
    A13_paper = 5    # E vs D
    A23_paper = 3    # F vs D

    w_paper, lmax_paper, ci_paper, cr_paper = ahp_3x3(A12_paper, A13_paper, A23_paper)

    print("Matrix from companion paper (E:F:D = 3:5; F:D = 3):")
    print(f"  a_EF={A12_paper}  a_ED={A13_paper}  a_FD={A23_paper}")
    print()
    print("Derived weights:")
    print(f"  w_E (Exposure)    = {w_paper[0]:.4f}   [paper claims 0.45]")
    print(f"  w_F (Feasibility) = {w_paper[1]:.4f}   [paper claims 0.35]")
    print(f"  w_D (Deadline)    = {w_paper[2]:.4f}   [paper claims 0.20]")
    print()
    print(f"  lambda_max = {lmax_paper:.4f}")
    print(f"  CI         = {ci_paper:.4f}")
    print(f"  CR         = {cr_paper:.4f}  (< 0.10 → matrix is consistent)")
    print()

    # ── What matrix WOULD produce 0.45 / 0.35 / 0.20? ────────────
    print("-" * 62)
    print("Back-calculation: what matrix produces 0.45 / 0.35 / 0.20?")
    print()
    # In AHP the weight ratio ≈ a_ij for consistent matrices.
    # So we need a_EF ≈ 0.45/0.35 ≈ 1.29, a_ED ≈ 0.45/0.20 ≈ 2.25, a_FD ≈ 0.35/0.20 ≈ 1.75
    r_EF = 0.45 / 0.35
    r_ED = 0.45 / 0.20
    r_FD = 0.35 / 0.20
    print(f"  Required a_EF ≈ {r_EF:.2f}  (paper uses {A12_paper})")
    print(f"  Required a_ED ≈ {r_ED:.2f}  (paper uses {A13_paper})")
    print(f"  Required a_FD ≈ {r_FD:.2f}  (paper uses {A23_paper})")
    print()
    w_implied, lmax_implied, ci_implied, cr_implied = ahp_3x3(r_EF, r_ED, r_FD)
    print("  Weights from implied matrix:")
    print(f"    w_E = {w_implied[0]:.4f}")
    print(f"    w_F = {w_implied[1]:.4f}")
    print(f"    w_D = {w_implied[2]:.4f}")
    print(f"    CR  = {cr_implied:.4f}")
    print()

    # ── Conclusion ────────────────────────────────────────────────
    print("=" * 62)
    print("CONCLUSION")
    print("=" * 62)
    print()
    print("The AHP matrix quoted in the companion paper (a_EF=3, a_ED=5,")
    print("a_FD=3) produces weights [0.633, 0.261, 0.106], NOT [0.45, 0.35,")
    print("0.20]. The weights in the paper are NOT derived from this matrix.")
    print()
    print("ACTION REQUIRED:")
    print("  Option A — Correct the matrix to produce the desired weights.")
    print("             Implied values: a_EF≈1.29, a_ED≈2.25, a_FD≈1.75.")
    print("             Note: Saaty's scale uses integer/half-integer values,")
    print("             so the closest consistent matrix would need rounding.")
    print("  Option B — Remove the AHP claim and describe weights as")
    print("             'author-assigned heuristic values' (already implemented")
    print("             in mrc_scorer.py and the manuscript draft).")
    print()
    print("Until a properly documented expert-elicitation is conducted, Option B")
    print("is the scientifically defensible choice.")
    print()


if __name__ == '__main__':
    main()
