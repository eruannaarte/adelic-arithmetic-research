"""Independent exact witnesses for transfer hypotheses and strict endpoints."""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import json

HERE = Path(__file__).resolve().parent


def dot(a, b):
    return sum((x * y for x, y in zip(a, b)), Q())


def apply(a, x):
    return [dot(row, x) for row in a]


def square(a, x):
    return dot(x, apply(a, x))


def encode(x):
    if isinstance(x, Q):
        return str(x)
    if isinstance(x, dict):
        return {k: encode(v) for k, v in x.items()}
    if isinstance(x, (tuple, list)):
        return [encode(v) for v in x]
    return x


def correlated_noise():
    W = [[Q(2), Q(1)], [Q(1), Q(2)]]
    invW = [[Q(2, 3), Q(-1, 3)], [Q(-1, 3), Q(2, 3)]]
    for j in range(2):
        assert apply(W, [invW[i][j] for i in range(2)]) == [Q(int(i == j)) for i in range(2)]
    error = [Q(4, 5), Q(-2, 5)]
    # The gradient in every discarded-coordinate direction is zero.
    assert apply(W, error)[1] == 0
    correct = Q(3, 2) * error[0] ** 2
    wrong = W[0][0] * error[0] ** 2
    assert square(W, error) == correct == Q(24, 25) < 1 < wrong
    return {'W': W, 'retention': [[Q(1), Q(0)]], 'actual_error': error,
            'retained_precision': Q(3, 2), 'minimum_original_noise_cost_squared': correct,
            'wrong_principal_precision_cost_squared': wrong}


def complex_correlated_noise():
    # Complex values are exact Gaussian rational pairs (real, imaginary).
    def add(x, y):
        return x[0] + y[0], x[1] + y[1]
    def mul(x, y):
        return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]
    def cj(x):
        return x[0], -x[1]
    W = [[(Q(2), Q(0)), (Q(0), Q(-1))], [(Q(0), Q(1)), (Q(2), Q(0))]]
    error = [(Q(4, 5), Q(0)), (Q(0), Q(-2, 5))]
    weighted = [add(mul(row[0], error[0]), mul(row[1], error[1])) for row in W]
    assert weighted[1] == (0, 0)
    cost = add(mul(cj(error[0]), weighted[0]), mul(cj(error[1]), weighted[1]))
    assert cost == (Q(24, 25), 0)
    assert W[0][1] == cj(W[1][0])
    return {'Hermitian_W_Gaussian_pairs': W, 'error_Gaussian_pairs': error,
            'noise_cost_squared_Gaussian_pair': cost, 'minimum_retained_precision': Q(3, 2)}


def quotient_order():
    P = [[Q(1, 2), Q(-1, 2)], [Q(-1, 2), Q(1, 2)]]
    y0, y1 = [Q(0), Q(0)], [Q(0), Q(2)]
    assert y0[0] == y1[0]
    assert apply(P, y0)[0] == 0 and apply(P, y1)[0] == -1
    # The retained first reading with common nuisance is x+z: a new alias.
    assert Q(0) + Q(0) == Q(1) + Q(-1)
    return {'nuisance_column': [Q(1), Q(1)], 'full_projector': P,
            'same_retained_data': [y0, y1], 'restricted_full_quotient_outputs': [Q(0), Q(-1)],
            'correct_retained_nuisance_free_dimension': 0}


def two_factorization_criteria():
    P = [[Q(1), Q(0), Q(0)], [Q(0), Q(1), Q(0)], [Q(0), Q(0), Q(0)]]
    y0, y1 = [Q(0)] * 3, [Q(0), Q(1), Q(0)]
    # AP=A, so restricted full-quotient data are computable from retained data.
    assert P[0] == [Q(1), Q(0), Q(0)]
    # But the entire full-data quotient is not computable from those data.
    assert y0[0] == y1[0] and apply(P, y0) != apply(P, y1)
    return {'full_projector': P, 'retention': [[Q(1), Q(0), Q(0)]],
            'restricted_quotient_factors_through_retention': True,
            'entire_quotient_factors_through_retention': False,
            'same_retained_data_with_distinct_full_quotients': [y0, y1]}


def query_saturation():
    observations = {'a0': (0, 0), 'a1': (0, 1), 'b0': (1, 0), 'b1': (1, 1)}
    query = {'a0': 0, 'a1': 0, 'b0': 1, 'b1': 1}
    witnesses = []
    for y in observations.values():
        original = {query[x] for x, value in observations.items() if value == y}
        reduced = {query[x] for x, value in observations.items() if value[0] == y[0]}
        assert original == reduced
        witnesses.append({'observation': y, 'answer': sorted(original)})
    assert observations['a0'] != observations['a1'] and observations['a0'][0] == observations['a1'][0]
    return {'sources': observations, 'query_labels': query, 'query_fibers_preserved': witnesses,
            'individual_source_fibers_preserved': False,
            'saturation_scope': 'relative to the four-point promised domain'}


def pointwise_vs_minimax():
    eta = Q(1)
    y = [Q(0), Q(3, 5)]
    full_radius = Q(4, 5)
    assert full_radius ** 2 + y[1] ** 2 == eta ** 2
    retained_only_candidate = Q(9, 10)
    assert retained_only_candidate ** 2 < eta ** 2
    assert retained_only_candidate ** 2 + y[1] ** 2 == Q(117, 100) > eta ** 2
    return {'observation': y, 'full_conditional_query_interval': [-full_radius, full_radius],
            'retained_conditional_query_interval': [-eta, eta],
            'both_uniform_minimax_radii': eta, 'candidate_admitted_only_after_restriction': retained_only_candidate}


def shared_stage_support():
    primitive_radius = Q(1)
    combined_coefficient = Q(1) + Q(-1)
    exact_support = abs(combined_coefficient) * primitive_radius
    product_relaxation = abs(Q(1)) + abs(Q(-1))
    assert exact_support == 0 and product_relaxation == 2
    # Under a genuine two-dimensional deterministic box the sum 2 is attained.
    independent_total = dot([Q(1), Q(1)], [Q(1), Q(1)])
    assert independent_total ** 2 == 4 > 2
    return {'shared_primitive_radius': primitive_radius, 'stage_coefficients': [Q(1), Q(-1)],
            'exact_composed_directional_budget': exact_support,
            'separate_error_set_budget': product_relaxation,
            'independent_box_sum_witness': independent_total,
            'quadrature_of_separate_unit_radii_is_unsafe_for_that_box': True}


def nuisance_leakage():
    epsilon, amplitude = Q(1, 1000), Q(2000)
    leakage = epsilon * amplitude
    assert leakage == 2 > 1
    return {'projector_matrix_error': epsilon, 'unrestricted_nuisance_amplitude_witness': amplitude,
            'resulting_output_leakage': leakage, 'violated_proposed_output_budget': Q(1),
            'scaling_formula_for_any_budget_K': 'choose amplitude=(K+1)/epsilon'}


def nonconvex_query_union():
    class0, class1 = [Q(-1), Q(1)], [Q(0)]
    distance = min(abs(a - b) for a in class0 for b in class1)
    assert distance == 1
    assert (class0[0] + class0[1]) / 2 == class1[0]
    # Both orientations of every nonzero scalar functional fail strict
    # separation of the convexified classes. The finite templates are disjoint.
    return {'query0_exact_responses': class0, 'query1_exact_responses': class1,
            'actual_pair_distance': distance, 'sharp_open_noise_threshold': distance / 2,
            'convexified_classes_overlap_at': Q(0)}


def source_tube_endpoint():
    # Orthogonal one-dimensional source maps have block Gram I_2.
    delta0, delta1 = Q(3, 5), Q(4, 5)
    a, b = Q(5, 4), Q(5, 3)
    common = [Q(4, 5), Q(3, 5)]
    e0 = [common[0] - a, common[1]]
    e1 = [common[0], common[1] - b]
    assert dot(e0, e0) == delta0 ** 2 * a ** 2
    assert dot(e1, e1) == delta1 ** 2 * b ** 2
    assert delta0 ** 2 + delta1 ** 2 == 1
    return {'block_Gram': [[Q(1), Q(0)], [Q(0), Q(1)]],
            'relative_radii': [delta0, delta1], 'source_amplitudes': [a, b],
            'common_observation_at_equality': common, 'legal_errors': [e0, e1],
            'consequence': 'strict pair-floor inequality cannot be weakened to equality in general'}


def build():
    return encode({'schema': 'independent-transfer-witnesses-v1',
                   'examples': {'correlated_retained_metric': correlated_noise(),
                                'Hermitian_retained_metric': complex_correlated_noise(),
                                'noncommuting_quotient': quotient_order(),
                                'distinct_factorization_criteria': two_factorization_criteria(),
                                'query_class_saturation': query_saturation(),
                                'pointwise_vs_minimax': pointwise_vs_minimax(),
                                'shared_stage_error_support': shared_stage_support(),
                                'unrestricted_nuisance_leakage': nuisance_leakage(),
                                'nonconvex_query_union': nonconvex_query_union(),
                                'closed_source_tube_endpoint': source_tube_endpoint()},
                   'status': 'PASS', 'scope': 'exact witnesses and finite algebraic controls; general theorems require the accompanying proofs'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    data = build()
    path = HERE / 'examples.json'
    if args.write:
        path.write_text(json.dumps(data, indent=2) + '\n')
    if data != json.loads(path.read_text()):
        raise ValueError('independent exact example replay mismatch')
    print('PASS: ten independent exact transfer witnesses')
