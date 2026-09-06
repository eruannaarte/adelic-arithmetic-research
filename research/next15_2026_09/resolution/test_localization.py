from copy import deepcopy
from fractions import Fraction as Q
from math import factorial
import unittest
import numpy as np
from flint import fmpq,fmpq_mat,arb,arb_mat,ctx
from localization import build,tail
from check_localization import check
from simulate import response


class LocalizationTests(unittest.TestCase):
    def test_certificate_and_adversarial_claims(self):
        c=build();self.assertTrue(check(c));self.assertEqual(c['depth'],47)
        for field,value in [('relative_output_noise','-1/10000'),('source_nonzero',False),('centroid_bias_upper','0')]:
            d=deepcopy(c);d[field]=value
            with self.assertRaises(AssertionError):check(d)
        d=deepcopy(c);d['relative_output_noise']='1/1000'
        with self.assertRaises(AssertionError):check(d)

    def test_first_moment_tail_identity(self):
        mu=Q(2,3);d=5
        finite=sum((Q(k)*mu**k/factorial(k) for k in range(d+1,60)),Q())
        self.assertLess(finite,mu*tail(mu,d))

    def test_infinite_symmetry_on_large_finite_control(self):
        n=61;j=30
        for u in [[1.,0.],[0.,1.],[.6,.8]]:
            y=response(n,j,u,tau=1.)
            self.assertLess(np.max(abs(y-y[::-1])),1e-14)
            self.assertAlmostEqual(np.arange(n)@abs(y)**2/(y@y),j,places=10)

    def test_centroid_noise_inequality_and_zero_obstruction(self):
        y=response(61,15,[.6,.8]);nu=1e-4
        for location in [0,30,60]:
            e=np.zeros(61);e[location]=nu*np.linalg.norm(y);z=y+e
            centroid=lambda a:np.arange(len(a))@abs(a)**2/(a@a)
            self.assertLessEqual(abs(centroid(z)-centroid(y)),60*(2*nu+nu**2)/(1-nu)**2)
        self.assertTrue(np.array_equal(response(15,3,[0.,0.]),response(15,11,[0.,0.])))


if __name__=='__main__':unittest.main()
