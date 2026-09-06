from copy import deepcopy
import unittest
import numpy as np
from window import build
from check_window import check
from simulate import response


class WindowTests(unittest.TestCase):
    def test_certificate_and_corruption(self):
        c=build();self.assertTrue(check(c));self.assertEqual(c['channel_count'],99)
        for field,value in [('channel_count',97),('information_loss_upper','0'),('relative_output_noise','1/10')]:
            d=deepcopy(c);d[field]=value
            with self.assertRaises(AssertionError):check(d)

    def test_discarded_gram_identity_and_psd(self):
        n=61;j=30;F=np.column_stack([response(n,j,[1.,0.]),response(n,j,[0.,1.])])
        window=np.arange(20,41);outside=np.setdiff1d(np.arange(n),window)
        loss=F[outside].T@F[outside]
        np.testing.assert_allclose(F.T@F-F[window].T@F[window],loss,atol=1e-18)
        self.assertGreaterEqual(np.linalg.eigvalsh(loss)[0],-1e-25)

    def test_two_symmetric_readouts_are_blind(self):
        n=61;j=30;F=np.column_stack([response(n,j,[1.,0.]),response(n,j,[0.,1.])])
        pair=F[[29,31]]
        np.testing.assert_allclose(pair[0],pair[1],atol=1e-17)
        null=np.array([pair[0,1],-pair[0,0]])
        self.assertGreater(np.linalg.norm(null),0)
        self.assertLess(np.linalg.norm(pair@null),1e-19)


if __name__=='__main__':unittest.main()
