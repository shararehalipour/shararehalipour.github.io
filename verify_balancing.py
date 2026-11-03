#!/usr/bin/env python3
"""Exhaustive small-instance checks for the exact balancing construction.

Python 3.10+, standard library only. The checks verify all subset pairs
through m=10 and every allowance in the theorem's range. The written
proof, not these finite tests, establishes the theorem for arbitrary m.
"""


def even_balance(x, m):
    """Balance a bitmask on an even ground set by one ordered scan."""
    assert m % 2 == 0
    n = m // 2
    size = x.bit_count()
    for i in range(m):
        bit = 1 << i
        if size < n and not x & bit:
            x |= bit
            size += 1
        elif size > n and x & bit:
            x ^= bit
            size -= 1
    assert size == n
    return x


def balance(x, m):
    if m % 2 == 0:
        return even_balance(x, m)
    n = (m + 1) // 2
    lifted = x | (1 << m) if x.bit_count() < n else x
    return even_balance(lifted, m + 1) & ((1 << m) - 1)


def separation(x, y):
    return max((x & ~y).bit_count(), (y & ~x).bit_count())


def check(m):
    size = 1 << m
    full = size - 1
    lo, hi = m // 2, (m + 1) // 2
    central = {x for x in range(size) if lo <= x.bit_count() <= hi}
    images = [balance(x, m) for x in range(size)]
    for x, image in enumerate(images):
        assert image in central, ("central image", m, x, image)
        assert images[full ^ x] == full ^ image, ("complements", m, x)
        if x in central:
            assert image == x, ("retraction", m, x, image)

    edge_pairs = nonexpanding_pairs = central_pairs = 0
    max_c = (m - 1) // 2
    for x in range(size):
        bx = images[x]
        for y in range(x):
            by = images[y]
            if m % 2 == 0:
                assert separation(bx, by) <= separation(x, y), (
                    "nonexpanding", m, x, y)
                nonexpanding_pairs += 1

            a = (x & y).bit_count()
            b = (full ^ (x | y)).bit_count()
            # This pair is an edge for exactly those allowed c >= max(a,b).
            # Checking its smallest eligible c implies all larger cases.
            first_c = max(1, a, b)
            if first_c <= max_c:
                assert bx != by, ("collapsed edge", m, x, y, first_c)
                assert (bx & by).bit_count() <= first_c, (
                    "image intersection", m, x, y, first_c)
                assert (full ^ (bx | by)).bit_count() <= first_c, (
                    "image complement intersection", m, x, y, first_c)
                edge_pairs += 1

            if m % 2 and x in central and y in central:
                infinity = 1 << m
                tx = x | infinity if x.bit_count() < hi else x
                ty = y | infinity if y.bit_count() < hi else y
                assert (tx & ty).bit_count() == max(a, b), (
                    "odd central identification", m, x, y)
                central_pairs += 1

    print(f"PASS m={m}: {size} subsets; {edge_pairs} pairs cover all "
          f"eligible c; {nonexpanding_pairs} nonexpansion pairs; "
          f"{central_pairs} odd central-layer identifications.")
    return edge_pairs, nonexpanding_pairs, central_pairs


def main():
    totals = [0, 0, 0]
    for m in range(2, 11):
        for i, count in enumerate(check(m)):
            totals[i] += count
    print("All complement, central-image, fixed-layer, adjacency, and "
          "listed metric/identification checks passed through m=10.")
    print(f"Totals: {totals[0]} eligible edge pairs; {totals[1]} even "
          f"nonexpansion pairs; {totals[2]} odd central-layer pairs.")
    print("Finite verification does not replace the proof for arbitrary m.")


if __name__ == "__main__":
    main()
