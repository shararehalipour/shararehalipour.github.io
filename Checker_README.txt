SUPPLEMENTARY FINITE CHECKS

The manuscript contains written proofs of its finite lemmas. These programs
provide reproducible checks of the specific finite data listed below; they do
not establish the homology or chain comparison theorems.

REQUIREMENTS AND COMMANDS

The first three programs require Python 3.10 or later and only its standard
library. From this directory, run:

    python3 verify_local_data.py
    python3 verify_balancing.py
    python3 check_appendixC_finite.py

The fourth program additionally requires python-sat and its Glucose3 backend.
It was tested with python-sat 1.9.dev17. For an isolated installation:

    python3 -m venv .venv
    .venv/bin/python -m pip install python-sat==1.9.dev17
    .venv/bin/python check_local_coloring_lemmas.py

On Windows, use .venv\Scripts\python.exe in place of .venv/bin/python.
The SAT solver is optional: it is not needed to run the other three programs
or to follow the written proofs. No UNSAT proof certificates are generated
or independently checked.

PROGRAMS AND CAPTURED OUTPUT

verify_local_data.py -> Verification_Results.txt
  Checks pentagon and rook incidence and matrix data; all 252 rook lists;
  both attachment tables, duality, and final forced-color deductions; all
  128 Fano assignments; the six-color construction for 2 <= n <= 6 and
  fourteen-color construction for 4 <= n <= 6; all 70 Fourier vectors and
  4,900 inner products; the exclusion bound on all 27,720 nonplane triples;
  all 367,290 nonplane quadruples and their full-cover/one-hole
  classifications (336 full covers and 8,624 one-hole families); the
  ten-center and four/five-center-cover conclusions; and the opposite-hole
  obstruction. In Appendix C this includes the classifications in C.2(b)
  and C.6(a), but does not explicitly check C.5.

verify_balancing.py -> Balancing_Verification.txt
  Checks every subset and every unordered pair of distinct subsets for
  2 <= m <= 10, throughout the theorem's allowance range. It checks central
  images, complement symmetry, fixed central layers, preservation of edges,
  the even scan's nonexpansion inequality, and the odd central-layer
  identification. The proof, rather than these bounded instances,
  establishes the theorem for arbitrary m.

check_appendixC_finite.py -> AppendixC_Verification.txt
  A separate implementation from the Appendix C definitions. Checks the
  Fourier inner-product identity, the 14 plane vectors, and exclusion
  cardinalities. Checks C.2(a) on all 54,740 triples of the 70 labels;
  C.5 (Majority center), including all three conclusions, on all 2,016
  triples with 11 exclusions; C.7 (Ten centers) for all 336 full-cover
  quadruples; and C.6(b) (Opposite holes) for all pairs of the 8,624
  one-hole families whose holes are complementary. All 367,290 nonplane
  quadruples are enumerated. For C.7, four- and five-center covers are
  checked directly, and C.2(a) rules out covers of size at most three.
  This program does not check the star classification C.2(b), the
  one-hole classification C.6(a), or every statement in C.1.

check_local_coloring_lemmas.py -> Local_Coloring_SAT_Verification.txt
  Encodes the local pentagon and rook coloring lemmas as SAT instances.
  Both rainbow-anchored systems are UNSAT. Each of the nine systems
  obtained by dropping one rook anchor is SAT (asserted as a control).
  It also checks both rook-list formulas on all 126 four-sets and the
  duality identities; thirteen individual lists and two set images are
  printed. The program verify_local_data.py directly asserts the
  displayed attachment-table deductions and the final set images.

SAT MODEL AND SCOPE

For every label S, phi(S) has exactly one color. For every label T, at
least one psi(T) value is selected, and every selected value is forbidden
from all phi(S) with |S intersection T| >= c. Allowing more than one psi
value does not weaken the check: any selected value can be chosen as the
missing color. Conversely any coloring with a missing color on every ball
satisfies the encoding after such a choice. Assuming the configuration is
rainbow permits its colors to be renamed so that phi(A_i)=i. Thus the SAT
encoding is equisatisfiable with the negation of the finite local lemma.
The program uses the solver's UNSAT result; it is not an independent
verification of a solver certificate.

LIMITATIONS

No program computes integral homology, checks the chain comparison theorem,
or audits the complete proof. Appendix C's structural lemmas C.3/C.4 and
its assembly argument C.8 are not machine-checked here. The scripts do not
check literature claims. Their printed counts state the finite ranges
actually enumerated and should not be read as a general proof certificate.
