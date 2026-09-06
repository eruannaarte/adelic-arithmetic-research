"""Independent KKT reconstruction of the real-rational transfer consumer."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'framework' / 'transfer.py'
spec = importlib.util.spec_from_file_location('transfer_consumer_under_audit', SOURCE)
consumer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(consumer)


def solve(a, rhs):
    """Independent exact elimination; no consumer algebra helpers are used."""
    n = len(rhs)
    rows = [[Q(v) for v in row] + [Q(b)] for row, b in zip(a, rhs)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if rows[i][j])
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = rows[j][j]
        rows[j] = [v / scale for v in rows[j]]
        for i in range(n):
            if i != j:
                scale = rows[i][j]
                rows[i] = [v - scale * w for v, w in zip(rows[i], rows[j])]
    return [row[-1] for row in rows]


def apply(a, x):
    return [sum((Q(v) * w for v, w in zip(row, x)), Q()) for row in a]


def kkt(W, R, B0, residual):
    n, m, k = len(W), len(R), len(B0[0])
    D = [[sum((Q(R[i][j]) * Q(B0[j][h]) for j in range(n)), Q()) for h in range(k)] for i in range(m)]
    K = []
    for i in range(n):
        K.append([Q(v) for v in W[i]] + [Q(0)] * k + [-Q(R[j][i]) for j in range(m)])
    for i in range(k):
        K.append([Q(0)] * (n + k) + [D[j][i] for j in range(m)])
    for i in range(m):
        K.append([Q(v) for v in R[i]] + D[i] + [Q(0)] * m)
    answer = solve(K, [Q(0)] * (n + k) + list(residual))
    noise, z = answer[:n], answer[n:n + k]
    nuisance = apply(D, z)
    assert [a + b for a, b in zip(apply(R, noise), nuisance)] == list(residual)
    return noise, nuisance, sum((a * b for a, b in zip(noise, apply(W, noise))), Q())


def build():
    cases = [
        ('correlated_noise', [[2, 1], [1, 2]], [[1, 0]], [[], []], [[], []]),
        ('shared_rank_deficient_nuisance', [[1, 0], [0, 4]], [[1, 0], [0, 1]], [[1, 2], [1, 2]], [[1], [1]]),
        ('coupled_rows_and_metric', [[3, 1, 0], [1, 2, 1], [0, 1, 3]], [[1, 0, 1], [0, 1, 1]], [[1, 2, 0], [0, 0, 0], [1, 2, 0]], [[1], [0], [1]]),
        ('discarded_nuisance', [[3, 1, 0], [1, 2, 1], [0, 1, 3]], [[1, 0, 0], [0, 0, 1]], [[0], [1], [0]], [[], [], []]),
        ('two_dimensional_rank_deficient_nuisance', [[2, 0, 0], [0, 3, 0], [0, 0, 5]], [[1, 0, 0], [0, 1, 0], [0, 0, 1]], [[0, 0, 0], [1, 0, 1], [0, 1, 1]], [[0, 0], [1, 0], [0, 1]])]
    counts = {}
    for name, W, R, B, B0 in cases:
        J = consumer.profile_form(W, R, B)['retained_profile_form']
        count = 0
        for entries in product(range(-2, 3), repeat=len(R)):
            residual = list(map(Q, entries))
            e, nuisance, cost = kkt(W, R, B0, residual)
            claimed = consumer.lifting_witness(W, R, B, residual)
            assert claimed['noise'] == e
            assert claimed['retained_nuisance'] == nuisance
            assert claimed['noise_squared'] == cost
            assert sum((a * b for a, b in zip(residual, apply(J, residual))), Q()) == cost
            count += 1
        counts[name] = count
    # Exact square-root-free cell condition checked against perfect-square
    # center/target floors, including the crucial negative residual branch.
    cells = 0
    for center_root, error, target_root in product(range(6), range(6), range(1, 6)):
        actual = consumer.continuous_cell_gate(center_root ** 2, error, target_root ** 2)
        assert actual == (center_root >= error + target_root)
        cells += 1
    return {'schema': 'independent-transfer-consumer-audit-v1',
            'consumer_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'KKT_case_counts': counts, 'total_exact_minimum_lift_checks': sum(counts.values()),
            'exact_cell_sign_and_endpoint_checks': cells, 'status': 'PASS',
            'scope': 'Independent rational constrained minimization and exact sign controls; mathematical proof reviewed separately.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    data = build()
    path = HERE / 'consumer_audit.json'
    if args.write:
        path.write_text(json.dumps(data, indent=2) + '\n')
    if data != json.loads(path.read_text()):
        raise ValueError('independent consumer audit replay mismatch')
    print(json.dumps(data, indent=2))
