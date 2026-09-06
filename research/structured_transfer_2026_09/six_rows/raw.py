"""Six exact raw readings, verified fourth-root normalization and unique decoding."""
from pathlib import Path
import importlib.util,argparse,json
from decoder import CertifiedBank
HERE=Path(__file__).resolve().parent
path=HERE.parents[1]/'refined_transfer_2026_09/normalization/normalize.py'
spec=importlib.util.spec_from_file_location('_six_verified_normalization',path)
normalization=importlib.util.module_from_spec(spec);spec.loader.exec_module(normalization)

class PhysicalBank(normalization.PhysicalBank):
    def __init__(self):
        self.name='6';self.decoder=CertifiedBank('6');self.summary=self.decoder.summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('data',type=Path);p.add_argument('--time',required=True);a=p.parse_args()
    print(json.dumps(PhysicalBank().decode(json.loads(a.data.read_text()),a.time),indent=2))
