"""Standard-library check of preserved history and validated artifact identity."""
from pathlib import Path
from fractions import Fraction as Q
import ast, hashlib, json, re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def check():
    history=json.loads((HERE/'PREVIOUS_ARTIFACTS_SHA256.json').read_text())
    assert len(history)==338
    for name,expected in history.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,'historical artifact changed: '+name
    validation=json.loads((HERE/'VALIDATION.json').read_text())
    assert validation['all_recorded_commands_passed'] is True
    for job in validation['jobs']:assert job['exit_code']==0,job['name']
    for name,expected in validation['validated_artifact_sha256'].items():
        assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==expected,'validated artifact changed: '+name
    for path in HERE.rglob('*.py'):ast.parse(path.read_text(),filename=str(path))
    for path in HERE.rglob('*.md'):
        contents=path.read_text()
        assert not any(ord(c)<32 and c not in '\n\t' for c in contents),'Markdown control character: '+str(path)
        for target in re.findall(r'\]\(([^)]+)\)',contents):
            if '://' in target or target.startswith('#'):continue
            target=target.split('#')[0].strip('<>')
            assert (path.parent/target).exists(),'broken local link: '+str(path)+' -> '+target
    for b,expected in [('8',1174),('9',1283)]:
        cert=json.loads((HERE/('resolution/certificate_'+b+'.json')).read_text())
        assert sum(len(c['records']) for c in cert['cells'])==expected
        out=json.loads((HERE/('resolution/checked_'+b+'.json')).read_text())
        assert out['whole_cell_records']==expected
        for profile in out['metrics'].values():
            assert Q(profile['source_relative_error_squared_upper'])<Q(profile['source_relative_accuracy_target'])**2
    doc=json.loads((HERE/'applications.json').read_text())
    assert (doc['whole_time_cell_transfer_gates'],doc['global_pair_and_inverse_profiles'],doc['arithmetic_coordinate_transfer_gates'])==(2457,7,196)
    for name,expected in doc['input_sha256'].items():
        assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==expected,'common adapter input changed: '+name
    for name in ('moderate','large'):
        data=json.loads((HERE/('noise/data_'+name+'.json')).read_text())
        assert len(data['readings'])==8900
        for design in ('multi','outer'):
            result=json.loads((HERE/('noise/result_'+design+'_'+name+'.json')).read_text())
            assert result['certificate']['answer_a1_through_a50']==data['truth_a1_through_a50']
    result={'verified':True,'historical_files_unchanged':len(history),
            'validated_artifact_hashes':len(validation['validated_artifact_sha256']),
            'python_syntax_and_local_links_checked':True,'recorded_focused_tests':17}
    print(json.dumps(result,indent=2));return result


if __name__=='__main__':check()
