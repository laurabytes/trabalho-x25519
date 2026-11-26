#!/usr/bin/env python3
"""Toy ECDLP experiment with idealized Fourier-sampling model.

This is NOT a complete quantum Shor circuit. It creates a small elliptic-curve
instance, evaluates the hidden scalar, and demonstrates idealized Fourier
sampling/post-processing on a finite cyclic subgroup.
"""
import argparse, json, random, math
from collections import Counter

def inv(a, p):
    return pow(a % p, -1, p)

def add(P, Q, a, p):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P; x2,y2=Q
    if x1 == x2 and (y1+y2) % p == 0: return None
    if P == Q:
        lam = ((3*x1*x1+a) * inv(2*y1,p)) % p
    else:
        lam = ((y2-y1) * inv(x2-x1,p)) % p
    x3=(lam*lam-x1-x2)%p
    y3=(lam*(x1-x3)-y1)%p
    return (x3,y3)

def mul(k, P, a, p):
    R=None
    while k:
        if k&1: R=add(R,P,a,p)
        P=add(P,P,a,p); k >>= 1
    return R

def point_order(P,a,p,limit=10000):
    R=None
    for n in range(1,limit+1):
        R=add(R,P,a,p)
        if R is None: return n
    raise ValueError("order not found")

def points(p,a,b):
    out=[]
    for x in range(p):
        for y in range(p):
            if (y*y - (x*x*x+a*x+b))%p==0:
                out.append((x,y))
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--p",type=int,default=17)
    ap.add_argument("--a",type=int,default=2)
    ap.add_argument("--b",type=int,default=2)
    ap.add_argument("--secret",type=int,default=3)
    ap.add_argument("--shots",type=int,default=4096)
    ap.add_argument("--seed",type=int,default=2026)
    ap.add_argument("--output",default="data/toy_ecdlog_results.json")
    args=ap.parse_args()
    if args.p < 5: raise SystemExit("p must be >= 5")
    pts=points(args.p,args.a,args.b)
    if (4*args.a**3+27*args.b**2)%args.p==0:
        raise SystemExit("Singular curve; choose different a,b,p")
    if not pts: raise SystemExit("No affine points")
    P=pts[0]
    r=point_order(P,args.a,args.p)
    d=args.secret%r
    if d==0: d=1
    Q=mul(d,P,args.a,args.p)
    # The subgroup relation is represented by the cyclic index j -> jP.
    # In this idealized model, Fourier outcomes concentrate on multiples
    # of M/r. We sample the corresponding ideal peaks, not a gate-level circuit.
    M=1
    while M < r*r: M*=2
    peaks=[round(k*M/r)%M for k in range(r)]
    rng=random.Random(args.seed)
    samples=[rng.choice(peaks) for _ in range(args.shots)]
    counts=Counter(samples)
    # Transparent recovery: solve Q=dP by exhaustive search in the toy subgroup.
    recovered=None
    R=None
    for candidate in range(r):
        if mul(candidate,P,args.a,args.p)==Q:
            recovered=candidate; break
    result={
      "model":"idealized_fourier_sampling_plus_classical_toy_ECDLP_validation",
      "not_a_full_shor_circuit":True,
      "curve":{"p":args.p,"a":args.a,"b":args.b},
      "P":P,"Q":Q,"secret_d":d,"subgroup_order":r,
      "field_size_bits":args.p.bit_length(),"subgroup_order_bits":r.bit_length(),
      "fourier_register_size_M":M,"shots":args.shots,"seed":args.seed,
      "measurement_counts":dict(sorted(counts.items())),
      "recovered_d_by_toy_exhaustive_validation":recovered,
      "success":recovered==d,
      "quantum_qubits":None,"circuit_depth":None,"total_gates":None,
      "two_qubit_gates":None,"execution_time_seconds":None,
      "limitations":[
        "No quantum circuit or quantum hardware is executed.",
        "Fourier outcomes are sampled from idealized peak locations.",
        "The scalar is validated by classical exhaustive search in a tiny group.",
        "This does not demonstrate recovery of a real X25519 secret."
      ]
    }
    import os
    os.makedirs(os.path.dirname(args.output) or ".",exist_ok=True)
    with open(args.output,"w") as f: json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))
if __name__=="__main__": main()
