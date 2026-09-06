"""Read-only preservation, evidence identity and manuscript consistency checks."""
from pathlib import Path
from fractions import Fraction as Q
import ast,hashlib,json,re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def check():
    history=json.loads((HERE/'PREVIOUS_ARTIFACTS_SHA256.json').read_text())
    assert len(history)==388
    for name,wanted in history.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==wanted,'historical artifact changed: '+name
    validation=json.loads((HERE/'VALIDATION.json').read_text())
    assert validation['all_recorded_checks_passed'] is True
    assert validation['focused_tests']=={'spatial':8,'normalization':8,'weighted_arithmetic':7,'total':23}
    for name,wanted in validation['validated_artifact_sha256'].items():
        assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==wanted,'validated artifact changed: '+name
    for p in HERE.rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
    for p in HERE.rglob('*.md'):
        text=p.read_text()
        assert not any(ord(c)<32 and c not in '\n\t' for c in text),'control character in '+str(p)
        assert text.count('\\[')==text.count('\\]'),'unbalanced display math in '+str(p)
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if '://' in target or target.startswith('#'):continue
            target=target.split('#')[0].strip('<>')
            assert (p.parent/target).exists(),'broken local link '+str(p)+' -> '+target
    cert=json.loads((HERE/'resolution/certificate_7.json').read_text())
    summary=json.loads((HERE/'resolution/checked_7.json').read_text())
    assert len(cert['cells'])==1051
    assert sum(len(c['records']) for c in cert['cells'])==3391
    assert summary['direct_rows']==[488,490,497,500,504,508,510]
    metric=summary['metrics']['L2']
    assert Q(metric['sensor_relative_radius'])==Q(1,10**7)
    assert Q(metric['source_relative_error_squared_upper'])<Q(1,10**6)
    packets=json.loads((HERE/'normalization/evidence.json').read_text())
    assert packets['verified'] and packets['case_count']==len(packets['cases'])==72
    assert len({(c['bank'],c['profile']) for c in packets['cases']})==8
    for c in packets['cases']:
        assert c['unique_recovered_label']==c['source_label']
        assert Q(c['source_relative_error_squared_upper'])<Q(c['source_relative_accuracy'])**2
    approximation=json.loads((HERE/'noise/checked_approximation.json').read_text())
    assert approximation['verified'] and approximation['polynomial_residual_bounds_checked']==24
    assert approximation['weighted_moment_bounds_checked']==6
    demo=json.loads((HERE/'noise/demonstration.json').read_text())
    assert demo['verified'] and demo['measurement_count']==8900 and Q(demo['family_amplitude'])==20000
    adapter=json.loads((HERE/'framework/applications.json').read_text())
    assert adapter['passed'] and adapter['successful_common_transfer_gates']==3509
    for name,wanted in adapter['input_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==wanted,'shared-theorem premise changed: '+name
    for p in (HERE/'review').glob('*.json'):
        d=json.loads(p.read_text());assert d.get('verified') is True,'review did not pass: '+str(p)
    output={'verified':True,'historical_files_unchanged':388,
            'validated_artifact_hashes':len(validation['validated_artifact_sha256']),
            'focused_tests_recorded':23,'common_transfer_gates_recorded':3509,
            'normalization_packets_recorded':72,'syntax_links_and_display_delimiters_checked':True}
    print(json.dumps(output,indent=2));return output


if __name__=='__main__':check()
