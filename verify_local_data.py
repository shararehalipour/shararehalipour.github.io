#!/usr/bin/env python3
"""Exact finite checks for the accompanying manuscript.

Python 3 standard library only. These checks do not compute integral homology
or verify the chain comparison theorem. They verify the finite incidence,
coloring, and Fourier data listed in the output.
"""
from itertools import combinations, product
from fractions import Fraction
from math import prod


def mask(s):
    return sum(1 << i for i in s)


def sets(N, k):
    return [mask(s) for s in combinations(range(N), k)]


def digits(s):
    return mask(int(x)-1 for x in str(s))


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def rank(rows):
    a = [list(map(Fraction, row)) for row in rows]
    r = 0
    for j in range(len(a[0])):
        pivot = next((i for i in range(r, len(a)) if a[i][j]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        q = a[r][j]
        a[r] = [x/q for x in a[r]]
        for i in range(len(a)):
            if i != r:
                q = a[i][j]
                a[i] = [x-q*y for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def configuration(c):
    q = 4*c+1
    if c == 1:
        adj = lambda i, j: (i-j) % 5 in (1, 4)
    else:
        adj = lambda i, j: i != j and (i//3 == j//3 or i%3 == j%3)
    A = [mask(j for j in range(q) if adj(i, j)) for i in range(q)]
    Z = [((1 << q)-1) ^ (A[i] | (1 << i)) for i in range(q)]
    M = [[int(adj(i, j)) for j in range(q)] for i in range(q)]
    for i, j in product(range(q), repeat=2):
        assert (A[i] & Z[j]).bit_count() == (0 if i == j else c)
        assert sum(M[i][k]*M[k][j] for k in range(q)) == c*(i == j)-M[i][j]+c
    assert rank(M) == q
    return A, Z


configuration(1)
A, Z = configuration(2)
print('PASS: pentagon and rook incidences, matrix identities, and exact ranks.')


def allowed(side, S):
    bases = Z if side == 'F' else A
    return {i+1 for i, B in enumerate(bases) if (S & B).bit_count() <= 1}


for S in sets(9, 4):
    rows = [(S & mask(range(3*a, 3*a+3))).bit_count() for a in range(3)]
    cols = [(S & mask(range(b, 9, 3))).bit_count() for b in range(3)]
    assert allowed('F', S) == {i+1 for i in range(9)
        if rows[i//3]+cols[i%3]-bool(S & (1 << i)) >= 3}
    assert allowed('G', S) == {i+1 for i in range(9)
        if rows[i//3]+cols[i%3]-2*bool(S & (1 << i)) <= 1}


def check_branch(initial, steps):
    known = {(s, digits(a)): v for s, a, v in initial}
    for side, ds, ds_list, exclusions, expected in steps:
        S = digits(ds)
        L = allowed(side, S)
        assert L == set(map(int, str(ds_list))), (side, ds, L)
        removed = set()
        for value, ws, wa in exclusions:
            W = digits(wa)
            assert ws != side and known[ws, W] == value
            assert (S & W).bit_count() >= 2
            assert value in L
            removed.add(value)
        remain = L-removed
        assert remain == (set() if expected is None else {expected})
        if expected is not None:
            known[side, S] = expected


check_branch([('F', 1234, 1), ('F', 5689, 5)], [
 ('G',1259,159,[(1,'F',1234),(5,'F',5689)],9),
 ('G',1369,158,[(1,'F',1234),(5,'F',5689)],8),
 ('F',2679,389,[(8,'G',1369),(9,'G',1259)],3),
 ('F',1789,789,[(8,'G',1369),(9,'G',1259)],7),
 ('G',3579,357,[(3,'F',2679),(5,'F',5689),(7,'F',1789)],None)])
check_branch([('F',1234,1),('F',5689,8)], [
 ('G',1456,189,[(1,'F',1234),(8,'F',5689)],9),
 ('G',1369,158,[(1,'F',1234),(8,'F',5689)],5),
 ('G',1368,168,[(1,'F',1234),(8,'F',5689)],6),
 ('F',3468,569,[(5,'G',1369),(6,'G',1368),(9,'G',1456)],None)])
pi = [((a+b) % 3)*3+(a-b) % 3 for a, b in product(range(3), repeat=2)]
assert len(set(pi)) == 9
perm = lambda S: mask(pi[i] for i in range(9) if S & (1 << i))
assert all(perm(A[i]) == Z[pi[i]] and perm(Z[i]) == A[pi[i]] for i in range(9))
assert perm(digits(1789)) == digits(1249) and pi[6]+1 == 9
assert perm(digits(1258)) == digits(1267) and pi[1]+1 == 6
for side, S, forbidden, prior, value in [
 ('G',1249,9,1234,4),('F',1247,1,1249,7),('G',1267,6,1247,2)]:
    previous = {1234:2,1249:4,1247:7}[prior]
    assert (digits(S)&digits(prior)).bit_count() >= 2
    assert allowed(side,digits(S))-{forbidden,previous} == {value}
assert (digits(1267)&digits(1234)).bit_count() == 2
print('PASS: all 252 rook lists, both attachment tables, duality, and final forced colors.')


fano = sorted({mask((u-1,v-1,(u^v)-1)) for u in range(1,8) for v in range(u+1,8)})
assert len(fano) == 7
for S in range(128):
    assert any((S & L) == L or (S & L) == 0 for L in fano)


def verify_coloring(n, blocks, threshold):
    full = (1 << (2*n))-1
    classes = {}
    for S in sets(2*n, n):
        color = next((i,side) for i,L in enumerate(blocks)
                     for side,T in ((1,S),(-1,S^full)) if (T & L) == L)
        classes.setdefault(color, []).append(S)
    for members in classes.values():
        for S,T in combinations(members,2):
            assert (S&T).bit_count() >= threshold


for n in range(2,7):
    verify_coloring(n,sets(3,2),2)
for n in range(4,7):
    verify_coloring(n,fano,3)
print('PASS: Fano monochromatic-line property (all 128 assignments); six/fourteen colorings through n=6.')

labels = sets(8,4)
char = lambda u,x: 1 if (u & x).bit_count() % 2 == 0 else -1
vec = {S: tuple(sum(char(u,x) for x in range(8) if S & (1 << x))//2
                for u in range(1,8)) for S in labels}
planes = [S for S in labels if any(abs(v)==2 for v in vec[S])]
nonplanes = [S for S in labels if S not in planes]
assert len(planes) == 14 and len(nonplanes) == 56
assert len(set(vec.values())) == 70
for S,T in product(labels,repeat=2):
    assert dot(vec[S],vec[T]) == 2*(S&T).bit_count()-4
for S in nonplanes:
    entries=[v for v in vec[S] if v]
    assert len(entries) == 4 and set(entries) <= {-1,1} and prod(entries) == -1
ex={S:mask(i for i,p in enumerate(planes) if dot(vec[S],vec[p]) < 0) for S in labels}
assert all(ex[S].bit_count()==4 for S in nonplanes)
assert max((ex[a]|ex[b]|ex[c]).bit_count() for a,b,c in combinations(nonplanes,3)) == 11
print('PASS: all 70 Fourier vectors and 4,900 inner products; all 27,720 nonplane triples have at most 11 exclusions.')

fullplanes=(1 << 14)-1
covers=[]
holes=[]
for family in combinations(nonplanes,4):
    E=ex[family[0]]|ex[family[1]]|ex[family[2]]|ex[family[3]]
    count=E.bit_count()
    if count == 14:
        assert all(sum(vec[S][j] for S in family)==0 for j in range(7))
        supports=[{j for j,v in enumerate(vec[S]) if v} for S in family]
        common=set.intersection(*supports)
        assert len(common)==1
        u0=next(iter(common))
        assert sorted(vec[S][u0] for S in family)==[-1,-1,1,1]
        for i,j in combinations(range(4),2):
            commonij=(supports[i]&supports[j])-{u0}
            assert len(commonij)==1
            u=next(iter(commonij))
            assert vec[family[i]][u] == -vec[family[j]][u]
        covers.append(family)
    elif count == 13:
        p=planes[(fullplanes^E).bit_length()-1]
        sign=1 if 2 in vec[p] else -1
        h=next(j for j,x in enumerate(vec[p]) if x)
        vectors=[tuple(sign*v for v in vec[S]) for S in family]
        d=[sum(v[j] for v in vectors) for j in range(7)]
        t1=d[h]==4 and sum(x*x for x in d)==16
        t2=d[h]==2 and sorted(abs(x) for x in d)==[0,0,0,0,0,2,2]
        if not (t1 or t2):
            assert rank(vectors)==4
            w=[sign*(sum(bool(S & (1 << x)) for S in family)-2) for x in range(8)]
            assert sorted(w)==[-1,0,0,0,0,0,0,1]
            positive=w.index(1);negative=w.index(-1)
            assert char(h+1,positive)==1 and char(h+1,negative)==-1
        holes.append((family,p))
print(f'PASS: all 367,290 nonplane quadruples; {len(covers)} full covers and {len(holes)} one-hole families satisfy their classifications.')

for family in covers:
    centers=[T for T in labels if all((S&T).bit_count()>=2 for S in family)]
    assert len(centers)==10 and all(T in nonplanes for T in centers)
    minimal=[]
    for C in combinations(centers,4):
        E=0
        for T in C:E|=ex[T]
        if E==fullplanes:minimal.append(frozenset(C))
    assert len(minimal)==2 and minimal[0].isdisjoint(minimal[1])
    for C in combinations(centers,5):
        E=0
        for T in C:E|=ex[T]
        assert (E==fullplanes)==any(F<=set(C) for F in minimal)
print(f'PASS: ten-center description and all four/five-center covers for every one of the {len(covers)} full-cover configurations.')

families_by_hole={p:[] for p in planes}
for family,p in holes:
    families_by_hole[p].append(mask(nonplanes.index(S) for S in family))
center_mask={S:mask(j for j,T in enumerate(nonplanes) if (S&T).bit_count()>=2)
             for S in nonplanes}
for family,p in holes:
    common=(1 << 56)-1
    for S in family:common &= center_mask[S]
    assert all((B&common)!=B for B in families_by_hole[p^255])
print('PASS: opposite-hole obstruction for every pair of one-hole families.')
print('All listed checks passed. Integral homology and the comparison theorem are not machine-checked here.')
