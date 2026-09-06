"""Exact finite quadratic-prefix realizability and constructive witnesses."""
from math import gcd, isqrt, prod
from itertools import product
import json
from pathlib import Path


def prime(n):
    return n >= 2 and all(n % d for d in range(2, isqrt(n)+1))


def primes(n): return [p for p in range(2,n+1) if prime(p)]


def legendre(a,p):
    r = pow(a % p,(p-1)//2,p)
    return -1 if r == p-1 else r


def chi(d,p):
    D = d if d % 4 == 1 else 4*d
    if p == 2:
        return 0 if D % 2 == 0 else (1 if D % 8 in (1,7) else -1)
    return legendre(D,p)


def prefix_from_signs(signs,n):
    a=[0]+[1]*n
    for k in range(2,n+1):
        v=k; out=1
        for p in primes(n):
            e=0
            while v%p == 0: e+=1; v//=p
            if e:
                if p not in signs: raise ValueError('missing local sign')
                out*=sum(signs[p]**j for j in range(e+1))
            if v==1: break
        a[k]=out
    return a[1:]


def valid_prefix(a):
    n=len(a)
    if n<1 or any(type(x) is not int for x in a) or a[0]!=1: return False
    ps=primes(n)
    if any(a[p-1] not in (0,1,2) for p in ps): return False
    return a == prefix_from_signs({p:a[p-1]-1 for p in ps},n)


def realize(signs,minimum_q=50):
    if any(not prime(p) or x not in (-1,0,1) for p,x in signs.items()):
        raise ValueError('prime signs must be -1,0,1')
    R=prod(p for p,x in signs.items() if x==0)
    residues=[]
    if signs.get(2)==0:
        residues.append((8,1))
    else:
        target=5 if signs.get(2)==-1 else 1
        residues.append((8,(target*pow(R,-1,8))%8))
    for p,x in sorted(signs.items()):
        if p==2: continue
        target=1 if x==0 else x*legendre(R,p)
        r=1 if target==1 else next(k for k in range(1,p) if legendre(k,p)==-1)
        residues.append((p,r))
    M=prod(m for m,r in residues)
    A=sum(r*(M//m)*pow(M//m,-1,m) for m,r in residues)%M
    assert gcd(A,M)==1
    q=A
    while q<=max([minimum_q,*signs.keys()]) or not prime(q): q+=M
    d=R*q; D=d if d%4==1 else 4*d
    assert d>1 and all(d%(p*p) for p in primes(isqrt(d)))
    assert all(chi(d,p)==x for p,x in signs.items())
    return {'signs':{str(p):x for p,x in signs.items()},'R':R,'residue':A,'modulus':M,'q':q,'d':d,'D':D}


if __name__=='__main__':
    examples=[realize(dict(zip((2,3,5),xs))) for xs in product((-1,0,1),repeat=3)]
    out=Path(__file__).resolve().parent/'quadratic_examples.json'
    out.write_text(json.dumps(examples,indent=2)+'\n')
    print(f'{len(examples)} exact field witnesses; maximum discriminant {max(x["D"] for x in examples)}')
