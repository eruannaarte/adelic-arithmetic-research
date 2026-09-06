"""Independent consequence checks, direct decoder control, and source mutation tests."""
import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from fractions import Fraction as Q
import numpy as np
import noise_certificate as nc
from check_consequences import check
from verify_mellin_certificate import _formal_projection
HERE=Path(__file__).resolve().parent


class Audit(unittest.TestCase):
    def test_standard_library_consequence_checker(self):
        self.assertTrue(check(json.loads((HERE/'certificate.json').read_text())))

    def test_rebuild_preserves_certified_result(self):
        self.assertEqual(nc.build(),json.loads((HERE/'certificate.json').read_text()))

    def test_direct_covariance_and_reused_reading_control(self):
        m=8900;j=np.arange(m);t=(2*j+1-m)/10;c=nc.REFERENCE_COEFFICIENTS
        long=(1+2*np.cos(2*np.pi*np.outer((j+.5)/m,np.arange(1,9)))@c)/m
        short=np.zeros(m);k=np.arange(2550)
        short[3175:5725]=(1+2*np.cos(2*np.pi*np.outer((k+.5)/2550,np.arange(1,9)))@c)/2550
        x=float(Q(125,65536));multi=x*short+(1-x)*long
        # Shared inner times are exactly the same physical measurements.
        np.testing.assert_array_equal(t[3175:5725],(2*k+1-2550)/10)
        correct=np.dot(multi,multi);wrong=x*x*np.dot(short,short)+(1-x)**2*np.dot(long,long)
        self.assertGreater(correct-wrong,1e-6)
        phi=np.exp(-1j*np.outer(t,np.log(np.arange(1,51))))
        cert=json.loads((HERE/'certificate.json').read_text());vv={}
        for name,w in [('multi',multi),('single',long)]:
            gram=phi.conj().T@(w[:,None]*phi)
            decoder=np.linalg.solve(gram,phi.conj().T*w[None,:])
            variances=np.sum(abs(decoder)**2,axis=1)*np.arange(1,51,dtype=float)**4
            bounds=np.array([[float(Q(a)),float(Q(b))] for a,b in cert['designs'][name]['variance_intervals']])
            self.assertTrue(np.all(variances>=bounds[:,0]) and np.all(variances<=bounds[:,1]))
            vv[name]=variances[-1]
        self.assertGreater(vv['multi']/vv['single'],1.0012)

    def test_stale_readdressed_and_wrong_contract_dependencies(self):
        original_root,original_single=nc.ROOT,nc.SINGLE
        with tempfile.TemporaryDirectory(prefix='path3-audit-') as tmp:
            root=Path(tmp);(root/'certificates').mkdir()
            remote_name='arithmetic_sensing_v_multiscale_T1780_remote.json'
            remote=json.loads((original_root/'certificates'/remote_name).read_text())
            source=json.loads(original_single.read_text())
            single=root/'single.json';single.write_text(json.dumps(source));nc.SINGLE=single;nc.ROOT=root
            try:
                (root/'certificates'/remote_name).write_text(json.dumps(remote))
                nc.source_bias(single)
                bad=copy.deepcopy(remote);bad['certificate']['degrees'][0]['remote_target_numerators']=['0']*50
                (root/'certificates'/remote_name).write_text(json.dumps(bad))
                with self.assertRaises(ValueError):nc.source_bias(single)
                bad['formal_certificate_sha256']=hashlib.sha256(nc.canonical(_formal_projection(bad['certificate']))).hexdigest()
                (root/'certificates'/remote_name).write_text(json.dumps(bad))
                with self.assertRaises(ValueError):nc.source_bias(single)
                bad=copy.deepcopy(remote);bad['certificate']['parameters']['observation_time']=510
                bad['formal_certificate_sha256']=hashlib.sha256(nc.canonical(_formal_projection(bad['certificate']))).hexdigest()
                source['certificate']['remote_dependency']['formal_certificate_sha256']=bad['formal_certificate_sha256']
                source['formal_certificate_sha256']=hashlib.sha256(nc.canonical(source['certificate'])).hexdigest()
                single.write_text(json.dumps(source));(root/'certificates'/remote_name).write_text(json.dumps(bad))
                with self.assertRaises(ValueError):nc.source_bias(single)
            finally:nc.ROOT=original_root;nc.SINGLE=original_single

    def test_vector_boundaries_and_rounding(self):
        for v,s in [(['0']*49,128),(['-1']*50,128),(['0']*50,127)]:
            with self.assertRaises(ValueError):nc.vector(v,s)
        # At a half-integer boundary nearest-integer recovery is not unique.
        margin=Q(1,2)-Q(1,2);self.assertEqual(margin,0)
        # Independent component noise would remove a strictly positive cross term;
        # that is a different acquisition model, never an allowed simplification.
        a,b,x=Q(2),Q(3),Q(1,7)
        self.assertEqual((x*a+(1-x)*b)**2-(x*x*a*a+(1-x)**2*b*b),2*x*(1-x)*a*b)

if __name__=='__main__':unittest.main(verbosity=2)
