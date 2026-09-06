"""Focused positive/negative controls for the Path 4 query certificate."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import json
import unittest
from unittest.mock import patch

import check_certificate as check
import query_certificate as producer
from flint import arb,ctx
from verified_end_to_end_certificate import verified_centered_response_interval

HERE=Path(__file__).resolve().parent


class QueryCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads((HERE/'certificate.json').read_text())
        cls.tails=[Q(x) for x in cls.doc['complete_tail_upper']]
        cls.rows=[Q(x) for x in cls.doc['gram_row_upper']]

    def test_independent_complete_consequence_check(self):
        self.assertTrue(check.check(self.doc)['verified'])
        self.assertEqual(producer.derive(self.tails,self.rows),self.doc['consequence'])

    def test_negative_noise_tail_and_gram_rejected(self):
        for tails,rows,eta in ((self.tails,self.rows,Q(-1)),
                               ([-Q(1)]+self.tails[1:],self.rows,Q()),
                               (self.tails,[-Q(1)]+self.rows[1:],Q())):
            with self.assertRaises(ValueError): producer.derive(tails,rows,eta)

    def test_unit_or_larger_gram_and_wrong_lengths_rejected(self):
        for q in (Q(1),Q(2)):
            with self.assertRaises(ValueError): producer.derive(self.tails,[q]+self.rows[1:])
        with self.assertRaises(ValueError): producer.derive(self.tails[:-1],self.rows)
        with self.assertRaises(ValueError): producer.derive(self.tails,self.rows+[Q()])

    def test_zero_noise_and_exact_query_threshold_boundary(self):
        self.assertTrue(producer.derive(self.tails,self.rows,Q())['all_pass'])
        c=producer.derive(self.tails,self.rows,Q(2004,100000))
        self.assertFalse(c['all_pass'])
        self.assertTrue(all(x['passes'] for x in c['anchors']))

    def test_declared_threshold_cannot_be_inflated(self):
        d=deepcopy(self.doc);d['consequence']['declared_eta']='1/10'
        with self.assertRaises(ValueError): check.check(d)

    def test_remote_domains_and_alias_boundary_rejected(self):
        for M,K in ((49,10**9),(10000,10000),(True,10**9),(10000,10**20),(50,10**9)):
            with self.assertRaises(ValueError): producer.remote_bound(M,K)

    def test_invalid_measure_weight_spacing_nesting_and_positivity(self):
        C=producer.VerifiedTimeComponent
        bads=((C(510,2550,Q(1,2)),),
              (C(511,2550,Q(1)),),
              (C(510,2550,Q(1,2)),C(511,2555,Q(1,2))),
              (C(510,2550,Q(-1)),C(1780,8900,Q(2))))
        for components in bads:
            with patch.object(producer,'COMPS',components):
                with self.assertRaises(ValueError): producer.measurement_contract()
        with patch.object(producer,'REFERENCE_COEFFICIENTS',[1.]):
            with self.assertRaises(ValueError): producer.measurement_contract()

    def test_remote_sine_mass_and_partition_corruption_rejected(self):
        for field,value in (('mass_above_M_upper','0'),('mass_above_K_upper','0'),('M',9999),('tail_upper','0')):
            d=deepcopy(self.doc);d['remote'][field]=value
            with self.assertRaises(ValueError): check.check(d)
        d=deepcopy(self.doc);d['remote']['component_bounds'][0]['sine_lower']='1'
        with self.assertRaises(ValueError): check.check(d)

    def test_incomplete_tail_and_wrong_query_algebra_rejected(self):
        d=deepcopy(self.doc);d['complete_tail_upper'][0]='0'
        with self.assertRaises(ValueError): check.check(d)
        d=deepcopy(self.doc);d['consequence']['query_cases'][0]['alpha'][0]='1'
        with self.assertRaises(ValueError): check.check(d)

    def test_outward_remote_precision_refinement(self):
        ctx.prec=256;r=producer.remote_bound()
        self.assertLessEqual(Q(r['tail_upper']),Q(self.doc['remote']['tail_upper']))
        self.assertEqual(check.check_remote(r,check.coefficients()),Q(r['tail_upper']))

    def test_exact_measure_against_raw_centered_grid(self):
        # Direct grid sum uses neither the response denominator identity nor
        # its common-numerator cancellation, and includes every grid point.
        ctx.prec=192
        coeff=producer.measurement_contract()
        T,m,_=check.COMPONENTS[0]
        frequency=(arb(51)/5).log();pi=arb.pi()
        mass=arb(0);response=arb(0)
        for j in range(m//2):
            theta=arb(2*j+1)/(2*m)
            weight=(1+2*sum((producer.ball(c)*(2*pi*r*theta).cos()
                            for r,c in enumerate(coeff,1)),arb(0)))/m
            self.assertTrue(weight>0)
            mass+=2*weight
            response+=2*weight*(T*(theta-arb(1)/2)*frequency).cos()
        self.assertTrue(mass.contains(1))
        lo,hi=producer.rational(response.lower()),producer.rational(response.upper())
        response_lo,response_hi=verified_centered_response_interval(5,51,T,m,precision=192)
        self.assertTrue(lo<=response_hi and response_lo<=hi)


if __name__=='__main__': unittest.main()
