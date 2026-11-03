"""Supplementary finite checks for Appendix C, derived from its definitions.

Run: python3 check_appendixC_finite.py (Python 3; standard library only).
Checks all triples for C.2(a), every extremal triple for C.5, every full-cover
quadruple for C.7, and every opposite-hole pair for C.6(b). Also checks the
Fourier inner-product identity, plane vectors, and exclusion cardinalities.
Does not compute homology or check the chain comparison theorem. Written
proofs establish the mathematical results; see Checker_README.txt for scope.
"""
from itertools import combinations
Omega = list(range(8))                       # F_2^3 as 3-bit integers
def chi(u, x): return -1 if bin(u & x).count('1') % 2 else 1
labels = [frozenset(c) for c in combinations(Omega, 4)]
def vec(A): return tuple(sum(chi(u, x) for x in A)//2 for u in range(1, 8))
V = {A: vec(A) for A in labels}
def dot(a, b): return sum(x*y for x, y in zip(a, b))
def xor_sum(A):
    s = 0
    for x in A: s ^= x
    return s
planes = [A for A in labels if xor_sum(A) == 0]
nonplanes = [A for A in labels if xor_sum(A) != 0]
assert len(planes) == 14 and len(nonplanes) == 56
# C.1(a): inner products
for A in labels:
    for Z in labels:
        assert dot(V[A], V[Z]) == 2*len(A & Z) - 4
# C.1(b): planes <-> +-2 e_u
for p in planes:
    nz = [v for v in V[p] if v]
    assert len(nz) == 1 and abs(nz[0]) == 2
def Ex(Z): return frozenset(p for p in planes if dot(V[p], V[Z]) < 0)
EX = {Z: Ex(Z) for Z in labels}
assert all(len(EX[Z]) == 4 for Z in nonplanes) and all(len(EX[p]) == 1 for p in planes)
# C.2(a)
assert max(len(EX[a] | EX[b] | EX[c]) for a, b, c in combinations(labels, 3)) == 11
print("C.1, C.2(a) re-derived: all triples of labels have at most 11 exclusions.")

# Lemma C.5 (majority center)
def centers_of(A): return [Z for Z in labels if len(A & Z) >= 2]
count = 0
for Z1, Z2, Z3 in combinations(labels, 3):
    E = EX[Z1] | EX[Z2] | EX[Z3]
    if len(E) != 11: continue
    count += 1
    assert all(Z in nonplanes for Z in (Z1, Z2, Z3))
    M = frozenset(x for x in Omega if sum(x in Z for Z in (Z1, Z2, Z3)) >= 2)
    assert len(M) == 4, (Z1, Z2, Z3, M)
    # (1): M is a center of every label of which Z1,Z2,Z3 are centers
    for A in labels:
        if all(len(A & Z) >= 2 for Z in (Z1, Z2, Z3)):
            assert len(A & M) >= 2
    # (2)
    assert EX[M] <= E
    # (3)
    for Zi, Zj in combinations((Z1, Z2, Z3), 2):
        assert len(EX[M] | EX[Zi] | EX[Zj]) < 11
    assert M not in (Z1, Z2, Z3)
print(f"Lemma C.5 verified on all {count} triples with 11 exclusions (M is a 4-set, and (1),(2),(3) hold).")

# Lemma C.7 and C.6(b) re-derived independently (brief)
P = frozenset(planes)
full = 0; holes = {}
for R in combinations(nonplanes, 4):
    E = EX[R[0]] | EX[R[1]] | EX[R[2]] | EX[R[3]]
    if len(E) == 14:
        full += 1
        cs = [Z for Z in labels if all(len(A & Z) >= 2 for A in R)]
        assert len(cs) == 10 and all(Z in nonplanes for Z in cs)
        four = [frozenset(C) for C in combinations(cs, 4) if len(frozenset().union(*(EX[Z] for Z in C))) == 14]
        assert len(four) == 2 and not (four[0] & four[1])
        for C in combinations(cs, 5):
            cov = len(frozenset().union(*(EX[Z] for Z in C))) == 14
            assert cov == any(F <= frozenset(C) for F in four)
    elif len(E) == 13:
        (q,) = tuple(P - E)
        holes.setdefault(q, []).append(frozenset(R))
print(f"Lemma C.7 verified on all {full} covering quadruples.")
comp = {p: frozenset(Omega) - p for p in planes}
bad = 0
for q, fams in holes.items():
    for A in fams:
        for Ap in holes.get(comp[q], []):
            if all(dot(V[a], V[b]) >= 0 for a in A for b in Ap):
                bad += 1
assert bad == 0
print(f"Lemma C.6(b) verified: no pair of one-hole families with opposite holes has all inner products >= 0 ({sum(len(v) for v in holes.values())} one-hole families).")
