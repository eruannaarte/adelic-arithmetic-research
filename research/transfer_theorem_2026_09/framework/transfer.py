"""Exact real rational consumers of the proved transfer contracts.

These routines check consequences of supplied bounds. Model producers must
establish their premises; an arbitrary positive matrix is not a model proof.
"""
from fractions import Fraction as F


def rational(value):
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError("Use exact integers, rational strings, or Fractions")
    if not isinstance(value, (int, str, F)):
        raise TypeError("Unsupported exact scalar")
    return F(value)


def matrix(value):
    if not isinstance(value, (list, tuple)) or not value:
        raise ValueError("Matrix must have at least one row")
    if not all(isinstance(row, (list, tuple)) for row in value):
        raise ValueError("Matrix rows are required")
    n = len(value[0])
    if any(len(row) != n for row in value):
        raise ValueError("Ragged matrix")
    return [[rational(x) for x in row] for row in value]


def transpose(a):
    return [list(col) for col in zip(*a)]


def multiply(a, b):
    if not a or not b or len(a[0]) != len(b):
        raise ValueError("Matrix product shape mismatch")
    return [[sum((a[i][k] * b[k][j] for k in range(len(b))), F(0))
             for j in range(len(b[0]))] for i in range(len(a))]


def subtract(a, b):
    if len(a) != len(b) or any(len(x) != len(y) for x, y in zip(a, b)):
        raise ValueError("Matrix subtraction shape mismatch")
    return [[x-y for x, y in zip(row, other)] for row, other in zip(a, b)]


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def inverse(a):
    a = matrix(a)
    n = len(a)
    if len(a[0]) != n:
        raise ValueError("Inverse requires square matrix")
    work = [row[:] + unit for row, unit in zip(a, identity(n))]
    for j in range(n):
        pivot = next((i for i in range(j, n) if work[i][j]), None)
        if pivot is None:
            raise ValueError("Singular matrix")
        work[j], work[pivot] = work[pivot], work[j]
        d = work[j][j]
        work[j] = [x/d for x in work[j]]
        for i in range(n):
            if i != j:
                d = work[i][j]
                work[i] = [x-d*y for x, y in zip(work[i], work[j])]
    return [row[n:] for row in work]


def rank(a):
    a = matrix(a)
    row = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(row, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[row], a[pivot] = a[pivot], a[row]
        d = a[row][col]
        a[row] = [x/d for x in a[row]]
        for i in range(row+1, len(a)):
            d = a[i][col]
            a[i] = [x-d*y for x, y in zip(a[i], a[row])]
        row += 1
        if row == len(a):
            break
    return row


def positive_definite(a):
    a = matrix(a)
    if len(a) != len(a[0]) or a != transpose(a):
        return False
    for k in range(len(a)):
        d = a[k][k]
        if d <= 0:
            return False
        for i in range(k+1, len(a)):
            for j in range(k+1, len(a)):
                a[i][j] -= a[i][k]*a[k][j]/d
    return True


def column_basis(a):
    a = matrix(a)
    columns = []
    for col in transpose(a):
        trial = transpose(columns+[col])
        if rank(trial) > len(columns):
            columns.append(col)
    return transpose(columns) if columns else [[] for _ in a]


def quadratic(a, v):
    v = [rational(x) for x in v]
    if len(a) != len(v) or any(len(row) != len(v) for row in a):
        raise ValueError("Quadratic form shape mismatch")
    return sum((v[i]*a[i][j]*v[j] for i in range(len(v))
                for j in range(len(v))), F(0))


def profile_form(w, restriction, nuisance):
    """Return the exact retained and full profiled forms for full-row-rank R.

    W must be SPD. B may be rank deficient or have zero columns. This real
    rational consumer rejects redundant R rows; the theorem covers them after
    retaining range consistency and using a pseudoinverse.
    """
    w, r, b = matrix(w), matrix(restriction), matrix(nuisance)
    n = len(w)
    if not positive_definite(w):
        raise ValueError("W must be symmetric positive definite")
    if len(r[0]) != n or len(b) != n:
        raise ValueError("Experiment dimensions mismatch")
    if rank(r) != len(r):
        raise ValueError("Retain an independent row basis and range consistency")
    winv = inverse(w)
    q = multiply(multiply(r, winv), transpose(r))
    h = inverse(q)
    c = column_basis(multiply(r, b))
    j = h
    if c[0]:
        hc = multiply(h, c)
        center = inverse(multiply(transpose(c), hc))
        j = subtract(h, multiply(multiply(hc, center), transpose(hc)))
    full = multiply(multiply(transpose(r), j), r)
    return {"retained_noise_form": h, "retained_profile_form": j,
            "full_profile_form": full, "nuisance_basis": c}


def lifting_witness(w, restriction, nuisance, residual):
    """An attained minimum-noise lift of a retained residual.

    The nuisance output is expressed in an independent retained column basis;
    the theorem guarantees its lift to an original unrestricted nuisance.
    """
    w, r, b = matrix(w), matrix(restriction), matrix(nuisance)
    residual = [rational(x) for x in residual]
    if len(residual) != len(r):
        raise ValueError("Retained residual dimension mismatch")
    forms = profile_form(w, r, b)
    h, c = forms["retained_noise_form"], forms["nuisance_basis"]
    rv = [[x] for x in residual]
    if c[0]:
        coeff = multiply(inverse(multiply(multiply(transpose(c), h), c)),
                         multiply(multiply(transpose(c), h), rv))
        nuisance_part = multiply(c, coeff)
    else:
        nuisance_part = [[F(0)] for _ in r]
    noise_part = subtract(rv, nuisance_part)
    e = multiply(multiply(multiply(inverse(w), transpose(r)), h), noise_part)
    ev = [row[0] for row in e]
    return {"noise": ev, "retained_nuisance": [row[0] for row in nuisance_part],
            "noise_squared": quadratic(w, ev)}


def scalar_boundary_squared(distance, support_sum, gain_squared):
    d, h, g2 = map(rational, (distance, support_sum, gain_squared))
    if d < 0 or h < 0 or g2 < 0:
        raise ValueError("Nonnegative distance, support, gain required")
    if d <= h:
        return {"separated_without_noise": False, "boundary_squared": F(0)}
    if g2 == 0:
        return {"separated_without_noise": True, "boundary_squared": None}
    return {"separated_without_noise": True,
            "boundary_squared": (d-h)**2/(4*g2)}


def strict_scalar_gate(distance, support_sum, gain_squared, radius):
    eta = rational(radius)
    if eta < 0:
        raise ValueError("Negative error radius")
    data = scalar_boundary_squared(distance, support_sum, gain_squared)
    return data["separated_without_noise"] and (
        data["boundary_squared"] is None or eta**2 < data["boundary_squared"])


def pair_gate(floor, first_budget, second_budget):
    lam, a, b = map(rational, (floor, first_budget, second_budget))
    if min(lam, a, b) < 0:
        raise ValueError("Nonnegative floor and error budgets required")
    return lam > a*a + b*b


def inverse_gate(floor, total_budget, relative_error):
    mu, d, r = map(rational, (floor, total_budget, relative_error))
    if min(mu, d, r) < 0:
        raise ValueError("Nonnegative inverse contract required")
    return mu > 0 and d*d < r*r*mu


def continuous_cell_gate(center_floor, operator_error, proposed_floor):
    """Check sqrt(center)>=error+sqrt(proposed), with a positive target."""
    c, e, p = map(rational, (center_floor, operator_error, proposed_floor))
    if c < 0 or e < 0 or p <= 0:
        raise ValueError("Nonnegative center/error and positive target required")
    residual = c-e*e-p
    return residual >= 0 and residual*residual >= 4*e*e*p


def normal_residual_error_bound(gram_floor, residual_bound):
    mu, r = map(rational, (gram_floor, residual_bound))
    if mu <= 0 or r < 0:
        raise ValueError("Positive Gram floor and nonnegative residual required")
    return r/mu
