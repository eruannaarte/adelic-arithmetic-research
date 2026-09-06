from pathlib import Path
from fractions import Fraction as F
from itertools import product
from copy import deepcopy
import importlib.util
import json
import sys
import unittest
import tempfile
from unittest.mock import patch
import numpy as np
import conditional_query as c
import geometry as g

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from arithmetic_sensing_iv import REFERENCE_COEFFICIENTS


class ConditionalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads((Path(__file__).parent/'conditional_query.json').read_text())

    def test_full_tail_replay_matches_and_all_strata_certify(self):
        self.assertTrue(c.check(self.doc)['verified'])
        replay=json.loads((Path(__file__).parent/'base_tail_replay.json').read_text())
        old=json.loads(c.SOURCE.read_text())
        self.assertEqual(replay,old)

    def test_exact_query_for_all_27_realizable_arithmetic_strata(self):
        for a2,a3,label in product(range(3),repeat=3):
            signs={p:-1 for p in g.PRIMES};signs.update({2:a2-1,3:a3-1,5:label-1})
            values=g.prefix(signs)
            eta=F(self.doc['strata'][3*a2+a3]['declared_eta'])
            self.assertEqual(c.decode(values,eta,self.doc),label)
            row=self.doc['strata'][3*a2+a3]
            self.assertEqual(sum(F(w)*values[n-1] for w,n in zip(row['alpha'],c.INDICES)),label)

    def test_raw_shared_grid_decoder_and_worst_noise_direction(self):
        m=8900;j=np.arange(m);t=(2*j+1-m)/10
        def weights(count):
            a=np.pi*(2*np.arange(count)+1)/count
            return (1+2*sum(float(x)*np.cos(k*a) for k,x in enumerate(REFERENCE_COEFFICIENTS,1)))/count
        wL=weights(m);wS=np.zeros(m);wS[3175:5725]=weights(2550)
        w=(125*wS+65411*wL)/65536
        Phi=np.exp(-1j*t[:,None]*np.log(np.arange(1,51))[None,:])
        D=np.arange(1,51,dtype=float)**2
        G=Phi.conj().T@(w[:,None]*Phi)
        A=D[:,None]*np.linalg.solve(G,Phi.conj().T*w)
        old=json.loads(c.SOURCE.read_text());q=float(F(old['consequence']['q']))
        for row in self.doc['strata']:
            alpha=np.zeros(50);alpha[np.array(c.INDICES)-1]=list(map(lambda x:float(F(x)),row['alpha']))
            raw=alpha@A;gain=np.sqrt(np.sum(np.abs(raw)**2/w))
            self.assertLessEqual(gain,(1/((1-q)*float(F(row['J']))))**.5)
            eta=F(row['declared_eta']);eps=float(eta)*raw.conj()/w/gain
            self.assertAlmostEqual(np.sqrt(np.sum(w*np.abs(eps)**2)),float(eta),places=13)
            for label in range(3):
                signs={p:-1 for p in g.PRIMES};signs.update({2:row['a2']-1,3:row['a3']-1,5:label-1})
                a=np.array(g.prefix(signs),dtype=float)
                # Finite-part interface control: the complete actual field tail is proved separately.
                estimated=A@(Phi@(a/D)+eps)
                self.assertEqual(c.decode(list(map(complex,estimated)),eta,self.doc),label)

    def test_decode_rejects_forged_certificate_before_lookup(self):
        signs={p:-1 for p in g.PRIMES};signs[5]=0
        genuine_prefix=g.prefix(signs)
        self.assertEqual(genuine_prefix[4],1)
        bad=deepcopy(self.doc);bad['strata'][0]['alpha']=['0']*7
        # Before the audit repair this direct call silently returned false label0.
        with self.assertRaises(ValueError):c.decode(genuine_prefix,0,bad)
        self.assertEqual(c.decode(genuine_prefix,0,self.doc),1)
        bad=deepcopy(self.doc);bad['strata'][0]['declared_eta']='1'
        with self.assertRaises(ValueError):c.decode(genuine_prefix,0,bad)

    def test_source_cache_is_by_content_and_returns_fresh_documents(self):
        original,digest=c.source()
        original['remote']['tail_upper']='0'
        fresh,new_digest=c.source()
        self.assertEqual(new_digest,digest)
        self.assertNotEqual(fresh['remote']['tail_upper'],'0')
        for field in ('remote','source'):
            bad=deepcopy(fresh)
            if field=='remote':bad['remote']['tail_upper']='0'
            else:bad['source']='independent coefficient envelope'
            with tempfile.TemporaryDirectory() as directory:
                path=Path(directory)/'certificate.json';path.write_text(json.dumps(bad))
                with patch.object(c,'SOURCE',path):
                    with self.assertRaises(ValueError):c.source()
        self.assertEqual(c.source()[1],digest)

    def test_bad_weights_budget_strata_and_comparison_rejected(self):
        for name in ('weights','budget','strata','comparison'):
            doc=deepcopy(self.doc)
            if name=='weights':doc['strata'][0]['alpha'][0]='0'
            elif name=='budget':doc['strata'][0]['declared_eta']='1/40'
            elif name=='strata':doc['strata'].pop()
            else:doc['strata'][8]['old_three_coordinate_radius_squared']='1/1000000'
            with self.assertRaises(ValueError):c.check(doc)
        self.assertIsNone(c.decode([1]*50,F(3,100),self.doc))
        with self.assertRaises(ValueError):c.decode([1]*49,0,self.doc)


if __name__=='__main__':unittest.main(verbosity=2)
