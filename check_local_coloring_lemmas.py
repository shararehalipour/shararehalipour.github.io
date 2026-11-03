"""Independent check of Lemma 3.3 (pentagon) and Lemma 4.2 (rook) via SAT.

Setting (paper, Sections 3.3 and 4.1): D a set of q = 4c+1 points carrying the
pentagon (c=1) or the 3x3 rook graph (c=2); A_i = neighbours of i (a 2c-set),
Z_i = D minus (A_i and i).  phi : binom(D,2c) -> [q] is a colouring of the labels,
and the hypothesis is that every ball B_c(Z) = {A : |A cap Z| >= c} misses a
colour psi(Z).  Claim: the A_i cannot be rainbow.

Run: python3 check_local_coloring_lemmas.py (Python 3 and python-sat).
Install dependency with: python3 -m pip install python-sat
Uses pysat.solvers.Glucose3; tested with python-sat 1.9.dev17. This is a
solver-backed supplementary check, without an independently checked UNSAT
certificate. It does not compute homology or verify the chain comparison.

Encoding: phi(S)=v, psi(T)=v as Boolean variables; each phi(S) takes exactly
one value, each psi(T) at least one value; phi(S) != psi(T) when |S cap T|>=c;
anchors phi(A_i)=i.  Expect UNSAT for both c=1 and c=2.  We also check that
dropping any single anchor makes the system SAT for c=2 (so the anchors are
all used), and we recompute the lists L(S), L*(T) of (8.3) from the definition.
"""
from itertools import combinations
from pysat.solvers import Glucose3
import sys

def rook():
    D = list(range(1, 10))
    def rc(i): return ((i-1)//3, (i-1) % 3)
    A = {i: frozenset(j for j in D if j != i and (rc(j)[0] == rc(i)[0] or rc(j)[1] == rc(i)[1])) for i in D}
    return D, A

def pentagon():
    D = list(range(1, 6))
    A = {i: frozenset({(i % 5) + 1, ((i - 2) % 5) + 1}) for i in D}
    return D, A

def build(c, drop_anchor=None):
    D, A = rook() if c == 2 else pentagon()
    q = len(D)
    Z = {i: frozenset(D) - A[i] - {i} for i in D}
    for i in D:
        assert len(A[i]) == 2*c and len(Z[i]) == 2*c and not (A[i] & Z[i])
        for j in D:
            if j != i:
                assert len(A[i] & Z[j]) == c, (i, j)
    labels = [frozenset(S) for S in combinations(D, 2*c)]
    idx = {}
    def var(kind, S, v):
        key = (kind, S, v)
        if key not in idx:
            idx[key] = len(idx) + 1
        return idx[key]
    s = Glucose3()
    for S in labels:
        s.add_clause([var('phi', S, v) for v in range(1, q+1)])
        for v in range(1, q+1):
            for w in range(v+1, q+1):
                s.add_clause([-var('phi', S, v), -var('phi', S, w)])
        s.add_clause([var('psi', S, v) for v in range(1, q+1)])
    for S in labels:
        for T in labels:
            if len(S & T) >= c:
                for v in range(1, q+1):
                    s.add_clause([-var('phi', S, v), -var('psi', T, v)])
    for i in D:
        if i == drop_anchor:
            continue
        s.add_clause([var('phi', A[i], i)])
    return s, D, A, Z, labels, q

for c in (1, 2):
    s, D, A, Z, labels, q = build(c)
    sat = s.solve()
    print(f"c={c}: anchored system satisfiable? {sat}  (expected False)")
    assert not sat
    if c == 2:
        # every anchor is needed?
        needed = []
        for i in D:
            s2, *_ = build(c, drop_anchor=i)
            needed.append(s2.solve())
        assert all(needed), "Every single-anchor deletion should be satisfiable"
        print("c=2: dropping one anchor gives SAT for each i:", needed)

# Recompute the lists of (8.2)/(8.3) for the rook graph from the definitions
D, A = rook()
Z = {i: frozenset(D) - A[i] - {i} for i in D}
def L(S):  return {i for i in D if len(S & Z[i]) <= 1}
def Ls(T): return {i for i in D if len(T & A[i]) <= 1}
def rc(i): return ((i-1)//3, (i-1) % 3)
def L_formula(S):
    out = set()
    for i in D:
        a, b = rc(i)
        ra = sum(1 for j in S if rc(j)[0] == a); cb = sum(1 for j in S if rc(j)[1] == b)
        if ra + cb - (1 if i in S else 0) >= 3: out.add(i)
    return out
def Ls_formula(T):
    out = set()
    for i in D:
        a, b = rc(i)
        ra = sum(1 for j in T if rc(j)[0] == a); cb = sum(1 for j in T if rc(j)[1] == b)
        if ra + cb - 2*(1 if i in T else 0) <= 1: out.add(i)
    return out
for S in combinations(D, 4):
    S = frozenset(S)
    assert L(S) == L_formula(S) and Ls(S) == Ls_formula(S)
fs = lambda s: ''.join(map(str, sorted(s)))
print("(8.3) agrees with the definitions on all 126 four-sets.")
for name, S in [('L(1234)', {1,2,3,4}), ('L(5689)', {5,6,8,9}), ('L*(1259)', {1,2,5,9}), ('L*(1369)', {1,3,6,9}),
                ('L(2679)', {2,6,7,9}), ('L(1789)', {1,7,8,9}), ('L*(3579)', {3,5,7,9}), ('L*(1456)', {1,4,5,6}),
                ('L*(1368)', {1,3,6,8}), ('L(3468)', {3,4,6,8}), ('L*(1249)', {1,2,4,9}), ('L(1247)', {1,2,4,7}),
                ('L*(1267)', {1,2,6,7})]:
    f = L if name.startswith('L(') else Ls
    print(f"{name} = {fs(f(frozenset(S)))}")
# duality permutation
pi = {}
for i in D:
    a, b = rc(i)
    pi[i] = 3*((a+b) % 3) + ((a-b) % 3) + 1
print("pi =", [pi[i] for i in D])
for i in D:
    assert frozenset(pi[j] for j in A[i]) == Z[pi[i]] and frozenset(pi[j] for j in Z[i]) == A[pi[i]]
print("pi(A_i)=Z_{pi(i)}, pi(Z_i)=A_{pi(i)} verified; pi(1789)=", fs(pi[j] for j in [1,7,8,9]), " pi(1258)=", fs(pi[j] for j in [1,2,5,8]))
