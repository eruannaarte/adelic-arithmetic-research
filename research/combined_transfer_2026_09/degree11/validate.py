"""Read-only artifact and exact-consequence verification for this package."""
from pathlib import Path
import hashlib,json
from check import check
from consequences import run as consequences
from orbit_comparison import run as orbit
HERE=Path(__file__).resolve().parent

def run():
    doc=json.loads((HERE/'VALIDATION.json').read_text())
    if doc['schema']!='degree-eleven-validation-v1':raise ValueError('validation schema')
    files={p.name:p for p in HERE.iterdir() if p.is_file() and p.name!='VALIDATION.json'}
    if set(files)!=set(doc['files_sha256']):raise ValueError('artifact coverage mismatch')
    for name,path in files.items():
        if hashlib.sha256(path.read_bytes()).hexdigest()!=doc['files_sha256'][name]:raise ValueError('artifact digest mismatch: '+name)
    check()
    if consequences()!=json.loads((HERE/'consequences.json').read_text()):raise ValueError('fixed contract changed')
    if orbit()!=json.loads((HERE/'orbit_comparison.json').read_text()):raise ValueError('combined orbit contract changed')
    return {'verified':True,'artifact_count':len(files),'exact_degree11_consequences':True,
            'meaning':'File identity and independent exact consequences verified; fresh physical replay commands remain available in README.'}
if __name__=='__main__':print(json.dumps(run(),indent=2))
