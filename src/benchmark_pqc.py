#!/usr/bin/env python3
"""Benchmark X25519 with Python cryptography and ML-KEM-768 via OpenSSL CLI.

OpenSSL CLI syntax varies by build. This script reports unsupported ML-KEM
operations as unavailable; it never substitutes fabricated timing values.
"""
import argparse, json, platform, shutil, subprocess, tempfile, time, statistics, os
from pathlib import Path

def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

def benchmark_x25519(n):
    try:
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    except Exception as e:
        return {"available":False,"reason":str(e)}
    keygen=[]; exchange=[]
    for _ in range(n):
        t=time.perf_counter_ns()
        a=X25519PrivateKey.generate(); b=X25519PrivateKey.generate()
        keygen.append((time.perf_counter_ns()-t)/1e6)
        ap=a.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
        bp=b.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
        t=time.perf_counter_ns(); ka=a.exchange(b.public_key()); kb=b.exchange(a.public_key())
        exchange.append((time.perf_counter_ns()-t)/1e6)
        if ka != kb: raise RuntimeError("X25519 shared secrets differ")
    return {"available":True,"repetitions":n,"public_key_bytes":32,"private_key_raw_bytes":32,
            "shared_secret_bytes":32,"keygen_pair_ms_median":statistics.median(keygen),
            "two_exchanges_ms_median":statistics.median(exchange),
            "note":"Python cryptography timings; includes wrapper/runtime overhead."}

def benchmark_mlkem(n):
    openssl=shutil.which("openssl")
    if not openssl: return {"available":False,"reason":"openssl executable not found"}
    ver=run([openssl,"version"])
    # Provider/CLI availability is build-dependent. Probe keygen help and
    # algorithm listing rather than assuming support.
    listing=run([openssl,"list","-kem-algorithms"])
    if listing.returncode != 0 or "ML-KEM-768" not in (listing.stdout+listing.stderr).upper():
        return {"available":False,"reason":"This OpenSSL build does not advertise ML-KEM-768 via list -kem-algorithms.",
                "openssl_version":ver.stdout.strip(),"probe":(listing.stdout+listing.stderr)[-1500:]}
    # OpenSSL 3.5 exposes ML-KEM through EVP APIs; CLI keygen/encap syntax
    # may not be available consistently. Do not claim a benchmark unless a
    # supported CLI workflow is found.
    return {"available":False,"reason":"ML-KEM-768 is advertised, but a portable CLI keygen/encap/decap workflow is not assumed by this script. Use the OpenSSL EVP API or liboqs binding and record separate timings.",
            "openssl_version":ver.stdout.strip(),"algorithm_listing":(listing.stdout+listing.stderr)[:3000]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repetitions",type=int,default=30)
    ap.add_argument("--output",default="data/benchmark_pqc.json")
    a=ap.parse_args()
    result={"platform":platform.platform(),"python":platform.python_version(),
            "x25519":benchmark_x25519(a.repetitions),"ml_kem_768":benchmark_mlkem(a.repetitions)}
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    Path(a.output).write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
if __name__=="__main__": main()
