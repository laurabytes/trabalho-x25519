#!/usr/bin/env python3
"""Simulação ideal de ECDLP reduzido pela estrutura de subgrupo oculto de Shor.

O estado é calculado exatamente em NumPy. Não é um circuito compilado em
portas nativas, não usa Aer/FakeProvider e não representa Curve25519 real.
"""
import argparse
import csv
import json
import math
import time
from pathlib import Path

import numpy as np


CASES = [
    {"name": "C4_F5", "p": 5, "a": 1, "b": 2, "P": (1, 2), "r": 4},
    {"name": "C8_F5", "p": 5, "a": 4, "b": 1, "P": (0, 1), "r": 8},
    {"name": "C16_F11", "p": 11, "a": 2, "b": 1, "P": (0, 1), "r": 16},
    {"name": "C32_F23", "p": 23, "a": 1, "b": 10, "P": (5, 5), "r": 32},
]


def point_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        if y1 % p == 0:
            return None
        slope = (3 * x1 * x1 + a) * pow(2 * y1, -1, p)
    else:
        slope = (y2 - y1) * pow((x2 - x1) % p, -1, p)
    slope %= p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def point_mul(k, P, a, p):
    result = None
    addend = P
    while k:
        if k & 1:
            result = point_add(result, addend, a, p)
        addend = point_add(addend, addend, a, p)
        k >>= 1
    return result


def point_order(P, a, p):
    current = None
    for order in range(1, 2 * p + 2):
        current = point_add(current, P, a, p)
        if current is None:
            return order
    raise ValueError("Não foi possível determinar a ordem do ponto.")


def qft_matrix(size):
    values = np.arange(size)
    return np.exp(2j * np.pi * np.outer(values, values) / size) / np.sqrt(size)


def run_case(case, secret, shots, seed):
    start = time.perf_counter()
    p, a, b = case["p"], case["a"], case["b"]
    P, r = case["P"], case["r"]
    if (4 * a**3 + 27 * b**2) % p == 0:
        raise ValueError(f"{case['name']}: curva singular.")
    if point_order(P, a, p) != r:
        raise ValueError(f"{case['name']}: ordem de P não confere.")

    d = secret % r
    if math.gcd(d, r) != 1:
        raise ValueError("O segredo de teste deve ser coprimo à ordem.")
    Q = point_mul(d, P, a, p)

    subgroup = [point_mul(k, P, a, p) for k in range(r)]
    labels = {point: index for index, point in enumerate(subgroup)}
    if len(labels) != r:
        raise ValueError("O ponto base não gera um subgrupo de ordem r.")

    # Cada bloco representa um valor do registrador de pontos após o oráculo.
    # O oráculo calcula f(u,v)=[u]P+[v]Q usando operações reais na curva.
    amplitudes = np.zeros((r, r, r), dtype=np.complex128)
    for u in range(r):
        uP = point_mul(u, P, a, p)
        for v in range(r):
            vQ = point_mul(v, Q, a, p)
            point = point_add(uP, vQ, a, p)
            amplitudes[labels[point], u, v] = 1 / r

    # Descartar o registrador de pontos equivale a somar probabilidades
    # dos resultados de Fourier condicionados a cada valor do ponto.
    fourier = qft_matrix(r)
    probabilities = np.zeros((r, r), dtype=float)
    for point_state in range(r):
        transformed = fourier @ amplitudes[point_state] @ fourier.T
        probabilities += np.abs(transformed) ** 2
    probabilities /= probabilities.sum()

    rng = np.random.default_rng(seed)
    samples = rng.multinomial(shots, probabilities.ravel()).reshape(r, r)
    recovered = []
    informative = 0
    relation_ok = 0
    for ku in range(r):
        for kv in range(r):
            count = int(samples[ku, kv])
            if count == 0:
                continue
            if (kv - d * ku) % r == 0:
                relation_ok += count
            if math.gcd(ku, r) == 1:
                informative += count
                candidate = (kv * pow(ku, -1, r)) % r
                recovered.extend([candidate] * count)

    if not recovered:
        raise RuntimeError(f"{case['name']}: nenhuma amostra informativa.")
    counts = {}
    for candidate in recovered:
        counts[candidate] = counts.get(candidate, 0) + 1
    recovered_d = max(counts, key=counts.get)
    elapsed = time.perf_counter() - start

    return {
        "name": case["name"],
        "curve": {"p": p, "a": a, "b": b},
        "P": list(P),
        "Q": list(Q),
        "order": r,
        "secret_d": d,
        "recovered_d": int(recovered_d),
        "success": recovered_d == d,
        "phase_qubits_each": int(math.log2(r)),
        "point_qubits": int(math.ceil(math.log2(r))),
        "logical_qubits": 3 * int(math.log2(r)),
        "shots": shots,
        "seed": seed,
        "informative_shots": informative,
        "informative_fraction": informative / shots,
        "theoretical_informative_fraction": sum(
            math.gcd(k, r) == 1 for k in range(r)
        ) / r,
        "period_relation_fraction": relation_ok / shots,
        "measurement_counts": [
            {"ku": u, "kv": v, "count": int(samples[u, v])}
            for u in range(r) for v in range(r) if samples[u, v]
        ],
        "simulation_seconds": elapsed,
        "method": "ideal_numpy_statevector_and_exact_qft",
        "limitations": [
            "Não é circuito nativo transpilado em Qiskit/Aer.",
            "O oráculo é uma tabela de valores da curva em instância pequena.",
            "A QFT é aplicada como matriz unitária exata.",
            "Não modela ruído, conectividade ou hardware quântico.",
            "Não quebra Curve25519 nem chaves X25519 reais."
        ]
    }


def main():
    parser = argparse.ArgumentParser(description="ECDLP reduzido: simulação ideal da estrutura de Shor.")
    parser.add_argument("--shots", type=int, default=4096)
    parser.add_argument("--secret", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20261110)
    parser.add_argument("--output", default="data/ecdlog_shor_results.json")
    parser.add_argument("--csv", default="data/ecdlog_shor_measurements.csv")
    args = parser.parse_args()
    if args.shots < 1:
        parser.error("--shots deve ser positivo.")

    results = [run_case(case, args.secret, args.shots, args.seed + i)
               for i, case in enumerate(CASES)]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")

    csv_path = Path(args.csv)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["case", "ku", "kv", "count"])
        writer.writeheader()
        for result in results:
            for item in result["measurement_counts"]:
                writer.writerow({"case": result["name"], **item})

    for result in results:
        print(f"{result['name']}: r={result['order']}, qubits={result['logical_qubits']}, "
              f"d={result['recovered_d']}, sucesso={result['success']}, "
              f"relação={result['period_relation_fraction']:.4f}")


if __name__ == "__main__":
    main()
