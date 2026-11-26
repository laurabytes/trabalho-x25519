#!/usr/bin/env python3
"""Circuito Qiskit de ECDLP reduzido: oráculo reversível por tabela e QFT."""
import argparse
import csv
import json
import math
import time
from pathlib import Path

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator

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
    result, addend = None, P
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
    raise ValueError("Ordem do ponto não encontrada.")


def inverse_qft(qc, register):
    """QFT inversa com convenção little-endian."""
    n = len(register)
    for i in range(n // 2):
        qc.swap(register[i], register[n - 1 - i])
    for j in reversed(range(n)):
        for k in reversed(range(j + 1, n)):
            qc.cp(-math.pi / (2 ** (k - j)), register[k], register[j])
        qc.h(register[j])


def build_ecdlog_circuit(case, secret):
    p, a, b, P, r = case["p"], case["a"], case["b"], case["P"], case["r"]
    if (4 * a**3 + 27 * b**2) % p == 0:
        raise ValueError("Curva singular.")
    if point_order(P, a, p) != r:
        raise ValueError("Ordem de P incompatível com a instância.")
    d = secret % r
    if math.gcd(d, r) != 1:
        raise ValueError("O escalar de teste deve ser coprimo à ordem.")
    Q = point_mul(d, P, a, p)
    n = int(math.log2(r))
    if 2**n != r:
        raise ValueError("Esta implementação requer ordem potência de dois.")

    u = QuantumRegister(n, "u")
    v = QuantumRegister(n, "v")
    point = QuantumRegister(n, "point")
    measured = ClassicalRegister(2 * n, "m")
    qc = QuantumCircuit(u, v, point, measured, name=f"ecdlog_{case['name']}")
    qc.h(u)
    qc.h(v)

    # Oráculo reversível: |u,v,z> -> |u,v,z XOR label([u]P+[v]Q)>.
    # A tabela é clássica, mas a consulta é implementada por portas controladas
    # em um circuito quântico explícito e reversível.
    subgroup = [point_mul(k, P, a, p) for k in range(r)]
    labels = {value: index for index, value in enumerate(subgroup)}
    if len(labels) != r:
        raise ValueError("P não gera um subgrupo cíclico da ordem declarada.")
    q_points = [point_mul(k, Q, a, p) for k in range(r)]
    controls = list(u) + list(v)
    for ui in range(r):
        uP = point_mul(ui, P, a, p)
        for vi in range(r):
            value = point_add(uP, q_points[vi], a, p)
            label = labels[value]
            if label == 0:
                continue
            control_state = ui | (vi << n)
            for bit in range(n):
                if (label >> bit) & 1:
                    qc.mcx(controls, point[bit], ctrl_state=control_state)

    inverse_qft(qc, u)
    inverse_qft(qc, v)
    for bit in range(n):
        qc.measure(u[bit], measured[bit])
        qc.measure(v[bit], measured[n + bit])
    metadata = {
        "name": case["name"], "curve": {"p": p, "a": a, "b": b},
        "P": list(P), "Q": list(Q), "order": r, "secret_d": d,
        "phase_qubits_each": n, "point_qubits": n,
        "logical_qubits": 3 * n,
    }
    return qc, metadata


def decode_counts(counts, n, secret, order):
    samples, informative = [], 0
    candidates = {}
    relation = 0
    for bitstring, count in counts.items():
        bits = bitstring.replace(" ", "")[::-1]
        ku = int(bits[:n], 2)
        kv = int(bits[n:2*n], 2)
        samples.append({"ku": ku, "kv": kv, "count": int(count)})
        if (kv - secret * ku) % order == 0:
            relation += int(count)
        if math.gcd(ku, order) == 1:
            informative += int(count)
            value = (kv * pow(ku, -1, order)) % order
            candidates[value] = candidates.get(value, 0) + int(count)
    recovered = max(candidates, key=candidates.get) if candidates else None
    total = sum(int(v) for v in counts.values())
    return recovered, samples, informative, relation, total


def run_case(case, secret, shots, seed, optimization_level=1):
    circuit, metadata = build_ecdlog_circuit(case, secret)
    backend = AerSimulator()
    start = time.perf_counter()
    compiled = transpile(
        circuit, backend=backend, optimization_level=optimization_level,
        seed_transpiler=seed,
    )
    transpile_seconds = time.perf_counter() - start
    start = time.perf_counter()
    result = backend.run(compiled, shots=shots, seed_simulator=seed).result()
    simulation_seconds = time.perf_counter() - start
    counts = result.get_counts(compiled)
    n = metadata["phase_qubits_each"]
    recovered, samples, informative, relation, total = decode_counts(
        counts, n, metadata["secret_d"], metadata["order"]
    )
    ops = compiled.count_ops()
    # Conta operações de dois qubits diretamente, sem inferir pela família do gate.
    two_qubit = sum(1 for inst in compiled.data if inst.operation.num_qubits == 2)
    metadata.update({
        "shots": shots, "seed": seed, "recovered_d": recovered,
        "success": recovered == metadata["secret_d"],
        "informative_shots": informative,
        "informative_fraction": informative / total if total else 0.0,
        "period_relation_fraction": relation / total if total else 0.0,
        "measurement_counts": samples,
        "transpiled_depth": compiled.depth(),
        "transpiled_total_operations": compiled.size(),
        "transpiled_two_qubit_operations": two_qubit,
        "transpiled_operation_counts": {str(k): int(v) for k, v in ops.items()},
        "transpile_seconds": transpile_seconds,
        "simulation_seconds": simulation_seconds,
        "backend": "AerSimulator ideal",
        "optimization_level": optimization_level,
        "oracle": "reversible multi-controlled-X table oracle",
        "limitations": [
            "Instância ECDLP reduzida em curva curta de Weierstrass.",
            "Oráculo reversível construído por tabela clássica; não é aritmética de curva escalável.",
            "AerSimulator ideal: sem ruído físico ou execução em QPU.",
            "Não quebra Curve25519 nem chaves X25519 reais.",
        ],
    })
    return metadata


def main():
    parser = argparse.ArgumentParser(description="ECDLP reduzido em circuito Qiskit/Aer.")
    parser.add_argument("--shots", type=int, default=4096)
    parser.add_argument("--secret", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20261126)
    parser.add_argument("--optimization-level", type=int, default=1, choices=range(4))
    parser.add_argument("--cases", nargs="+", default=[c["name"] for c in CASES])
    parser.add_argument("--output", default="data/ecdlog_qiskit_results.json")
    parser.add_argument("--csv", default="data/ecdlog_qiskit_measurements.csv")
    args = parser.parse_args()
    if args.shots < 1:
        parser.error("--shots deve ser positivo.")
    selected = [c for c in CASES if c["name"] in args.cases]
    if len(selected) != len(set(args.cases)):
        parser.error("Nome de instância desconhecido ou duplicado.")
    results = [run_case(c, args.secret, args.shots, args.seed + i,
                        args.optimization_level) for i, c in enumerate(selected)]
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    csv_path = Path(args.csv)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["case", "ku", "kv", "count"])
        writer.writeheader()
        for item in results:
            for sample in item["measurement_counts"]:
                writer.writerow({"case": item["name"], **sample})
    for item in results:
        print(f"{item['name']}: r={item['order']} d={item['recovered_d']} "
              f"success={item['success']} depth={item['transpiled_depth']} "
              f"ops={item['transpiled_total_operations']} 2Q={item['transpiled_two_qubit_operations']}")


if __name__ == "__main__":
    main()
