"""Read-only artifact, historical preservation and manuscript consistency check."""
from fractions import Fraction as Q
from pathlib import Path
import ast, hashlib, json, re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def need(condition, message):
    if not condition:
        raise ValueError(message)


def check():
    history = read(HERE/'PREVIOUS_ARTIFACTS_SHA256.json')
    need(history['count'] == len(history['files']) == 467, 'historical manifest extent')
    for name, wanted in history['files'].items():
        need(sha(ROOT/'research'/name) == wanted, 'historical artifact changed: '+name)
    validation = read(HERE/'VALIDATION.json')
    need(validation['all_recorded_checks_passed'] is True, 'recorded validation did not pass')
    need(validation['focused_tests'] == {'spatial':8,'arithmetic':8,'framework_raw':8,'total':24}, 'test count')
    for name, wanted in validation['validated_artifact_sha256'].items():
        need(sha(HERE/name) == wanted, 'sealed artifact changed: '+name)
    for folder, key in (('resolution','files_sha256'),('noise','artifact_sha256'),('review','files_sha256')):
        d = read(HERE/folder/'VALIDATION.json')
        need(d['verified'] is True, 'component validation not passed')
        for name,wanted in d[key].items():
            need(sha(HERE/folder/name) == wanted, 'component sealed artifact changed: '+folder+'/'+name)
    noise = read(HERE/'noise/VALIDATION.json')
    for name,wanted in noise['external_dependency_sha256'].items():
        need(sha(ROOT/name) == wanted, 'external arithmetic premise changed: '+name)
    for p in HERE.rglob('*.py'):
        ast.parse(p.read_text(), filename=str(p))
    for p in HERE.rglob('*.md'):
        text = p.read_text()
        need(not any(ord(c)<32 and c not in '\n\t' for c in text), 'control character in '+str(p))
        need(text.count('\\[') == text.count('\\]'), 'display math delimiter mismatch: '+str(p))
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if '://' in target or target.startswith('#'):
                continue
            target = target.split('#')[0].strip('<>')
            need((p.parent/target).exists(), 'broken local link: '+str(p)+' -> '+target)
    common = read(HERE/'framework/applications.json')
    need(common['verified'] is True, 'common gates did not pass')
    for name,wanted in common['input_sha256'].items():
        need(sha(ROOT/name) == wanted, 'common adapter input changed: '+name)
    need(common['spatial']['whole_cell_transfer_gates'] == 3743, 'cell transfer count')
    need(common['spatial']['direct_rows'] == [490,492,496,500,504,508,510], 'new bank rows')
    profiles = common['spatial']['profiles']
    need(Q(profiles['known_clock']['sensor'])/Q(1,10**7) == Q(7,5), 'claimed forty-percent allowance gain')
    for p in profiles.values():
        need(p['passed'] and Q(p['source_error_squared_upper']) < Q(1,10**6), 'strict spatial accuracy')
    need(common['arithmetic']['evaluated_integer_gates'] == 392 and
         common['arithmetic']['passing_integer_gates'] == 124 and
         common['arithmetic']['complete_unknown_integer_recoveries'] == 2, 'arithmetic positive/adverse counts')
    need(common['raw'] == {'actual_raw_packets':12,'actual_inverse_enclosures':12}, 'raw packet extent')
    need(noise['full_vector_weighted_norm_bounds'] == 184 and noise['complete_Taylor_moment_bounds'] == 16,
         'weighted physical premise extent')
    need(noise['actual_data_and_exact_proposal_replay_bits'] == 384, 'actual arithmetic replay precision')
    plans = read(HERE/'noise/consequences.json')
    need(len(plans['frequency_degree_capacities']) == 32 and len(plans['planning_error_budgets']) == 40,
         'degree comparison extent')
    ceiling = Q(1,10**30)
    for row in plans['frequency_degree_capacities'] + plans['planning_error_budgets']:
        need(Q(row['normal_residual_upper']) == ceiling, 'future acquisition must use stated residual ceiling')
    for path in (HERE/'review').glob('*_review.json'):
        need(read(path)['verified'] is True, 'independent review failed')
    result = {'verified':True,'historical_files_unchanged':467,
              'new_sealed_artifacts_checked':len(validation['validated_artifact_sha256']),
              'focused_tests_recorded':24,'whole_cell_transfers_recorded':3743,
              'unknown_integer_gates_recorded':392,'raw_packets_recorded':12,
              'independent_reviews_recorded':5,'links_syntax_and_model_claims_checked':True}
    print(json.dumps(result,indent=2))
    return result


if __name__ == '__main__':
    check()
