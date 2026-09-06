"""Read-only preservation, evidence identity and presentation consistency."""
from pathlib import Path
from fractions import Fraction as Q
import ast,hashlib,json,re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
def need(test,message):
    if not test:raise ValueError(message)


def check():
    history=read(HERE/'PREVIOUS_ARTIFACTS_SHA256.json')
    need(history['count']==len(history['files'])==553,'historical extent')
    for name,wanted in history['files'].items():
        need(sha(ROOT/'research'/name)==wanted,'historical artifact changed: '+name)
    validation=read(HERE/'VALIDATION.json')
    need(validation['all_recorded_checks_passed'] is True,'validation status')
    need(validation['focused_tests']=={'potential':10,'six_rows':8,'arithmetic':8,'shared':6,'total':32},'focused test counts')
    for name,wanted in validation['validated_artifact_sha256'].items():
        need(sha(HERE/name)==wanted,'new artifact changed: '+name)
    for folder,key in [('resolution','files_sha256'),('six_rows','files_sha256'),('arithmetic','artifact_sha256')]:
        component=read(HERE/folder/'VALIDATION.json')
        need(component['verified'] is True,'component status')
        for name,wanted in component[key].items():
            need(sha(HERE/folder/name)==wanted,'component artifact changed: '+folder+'/'+name)
    for name,wanted in read(HERE/'arithmetic/VALIDATION.json')['external_dependency_sha256'].items():
        need(sha(ROOT/name)==wanted,'external arithmetic premise changed: '+name)
    for p in HERE.rglob('*.py'):
        ast.parse(p.read_text(),filename=str(p))
    for p in HERE.rglob('*.md'):
        body=p.read_text()
        need(not any(ord(c)<32 and c not in '\n\t' for c in body),'control character: '+str(p))
        need(body.count('\\[')==body.count('\\]'),'math delimiters: '+str(p))
        for target in re.findall(r'\]\(([^)]+)\)',body):
            if '://' in target or target.startswith('#'):continue
            target=target.split('#')[0].strip('<>')
            need((p.parent/target).exists(),'broken local link: '+str(p)+' -> '+target)
    app=read(HERE/'framework/applications.json')
    need(app['verified'] is True,'common adapter')
    for name,wanted in app['input_sha256'].items():
        need(sha(ROOT/name)==wanted,'common premise changed: '+name)
    need(app['six_rows']['records']==1278 and app['six_rows']['raw_cases']==60,'six-row extent')
    need(Q(app['six_rows']['source_error_squared_upper'])<Q(852151,10**9)**2,'six-row reported accuracy')
    need(app['spatial']['direction_cells']==2688 and app['spatial']['raw_cases']==12,'potential extent')
    need(Q(app['spatial']['potential_radius'])==Q(1,400000),'potential tolerance')
    need(app['spatial']['directional_gate']['passed'] and not app['spatial']['directional_gate']['uniform_accuracy'],'directional consequence')
    need(Q(read(HERE/'resolution/checked.json')['source_relative_error_upper'])<Q(801020,10**9),'potential reported accuracy')
    need(app['arithmetic']['total_actual_future_comparison_gates']==980 and app['arithmetic']['least_tested_passing_degree']==12,'arithmetic extent')
    for row in app['arithmetic']['enlarged_clock_results']:
        need(row['new_passing_gates']==49,'new integer recovery')
        threshold=Q(447818,10**6) if row['design']=='multi' else Q(496864,10**6)
        need(Q(row['complete_coefficient_error_upper'])<threshold,'reported enlarged-clock error')
    review=read(HERE/'review/clock_review.json')
    need(review['verified'] and review['clock_bound_sha256']==sha(HERE/'arithmetic/clock_bound.json'),'independent complete-clock review')
    for row in review['results']:
        need(Q(row['base_clock_radius'])<Q(6416861,10**14),'reported full clock radius')
    six=read(HERE/'six_rows/VALIDATION.json')
    need(six['previous_seven_bank_deletion_obstructions']==7,'deletion obstruction extent')
    result={'verified':True,'historical_files_unchanged':553,
            'sealed_new_artifacts':len(validation['validated_artifact_sha256']),
            'focused_tests_recorded':32,'six_row_time_records':1278,
            'potential_direction_cases':2688,'raw_spatial_examples':72,
            'arithmetic_gate_comparisons':980,'links_syntax_and_report_claims_checked':True}
    print(json.dumps(result,indent=2));return result


if __name__=='__main__':check()
