#!/usr/bin/env python3
"""Create a transparent size comparison and one-million-session scenario."""
import csv
from pathlib import Path
import matplotlib.pyplot as plt

# Byte lengths from RFC 7748 and NIST FIPS 203.
rows=[
 ["Public key", "X25519", 32, "ML-KEM-768", 1184],
 ["Private key", "X25519 raw scalar", 32, "ML-KEM-768 decapsulation key", 2400],
 ["Encapsulation/message", "X25519 ephemeral public key", 32, "ML-KEM-768 ciphertext", 1088],
 ["Shared secret", "X25519", 32, "ML-KEM-768", 32],
]
out=Path("data"); out.mkdir(exist_ok=True)
with (out/"size_comparison.csv").open("w",newline="") as f:
    w=csv.writer(f); w.writerow(["metric","classic_item","classic_bytes","pqc_item","pqc_bytes","difference_bytes","increase_percent"])
    for metric,ci,cb,pi,pb in rows:
        w.writerow([metric,ci,cb,pi,pb,pb-cb,round((pb-cb)/cb*100,2)])
# Illustrative single-message comparison: one X25519 public value vs one KEM ciphertext.
n=1_000_000
classic=32*n; pqc=1088*n
with (out/"communication_scenario.csv").open("w",newline="") as f:
    w=csv.writer(f); w.writerow(["sessions","x25519_bytes","ml_kem_768_bytes","additional_bytes"])
    w.writerow([n,classic,pqc,pqc-classic])
plt.figure(figsize=(8,5))
plt.bar(["X25519 public value","ML-KEM-768 ciphertext"],[classic/1e9,pqc/1e9])
plt.ylabel("GB for 1,000,000 sessions (decimal)")
plt.title("Illustrative communication payload comparison")
plt.tight_layout()
Path("figures").mkdir(exist_ok=True)
plt.savefig("figures/communication_1m.png",dpi=180)
print(f"X25519 payload: {classic:,} bytes")
print(f"ML-KEM-768 payload: {pqc:,} bytes")
print(f"Difference: {pqc-classic:,} bytes ({(pqc-classic)/1e9:.3f} GB)")
