"""Deterministic standalone lab and Website Manager publication bundles."""
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
LAB=ROOT/'website/transfer-theorem-lab'
def write_zip(path,files):
    with ZipFile(path,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
        for name,source in sorted(files.items()):
            info=ZipInfo(name,date_time=(2026,9,5,0,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,source.read_bytes())
    return {'name':path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def main(output):
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    serving=['index.html','transfer.css','core.js','app.js','evidence.js','evidence.json','lab-manifest.json','README.md']
    files={n:LAB/n for n in serving};files.update({n:ROOT/n for n in ('LICENSE','LICENSE-CONTENT.md')})
    files['CITATION.cff']=ROOT/'publication/transfer-theorem-v1/CITATION.cff'
    receipts=[write_zip(output/'Transfer-Theorem-Lab-v1.zip',files)]
    selected=[ROOT/'TRANSFER_THEOREM_PUBLIC_COMPANION.md',ROOT/'LICENSE',ROOT/'LICENSE-CONTENT.md']
    selected+=sorted(p for p in LAB.iterdir() if p.is_file())
    selected+=sorted(p for p in (ROOT/'publication/transfer-theorem-v1').iterdir() if p.is_file())
    receipts.append(write_zip(output/'Transfer-Theorem-Publication-v1.zip',{p.relative_to(ROOT).as_posix():p for p in selected}))
    print(json.dumps(receipts,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output');args=p.parse_args();main(args.output)
