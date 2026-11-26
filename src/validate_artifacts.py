#!/usr/bin/env python3
"""Valida consistência estrutural dos resultados ECDLP e arquivos CSV."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
results_path = ROOT / "data/ecdlog_shor_results.json"
measurements_path = ROOT / "data/ecdlog_shor_measurements.csv"
qiskit_results_path = ROOT / "data/ecdlog_qiskit_results.json"
qiskit_measurements_path = ROOT / "data/ecdlog_qiskit_measurements.csv"


def main():
    results = json.loads(results_path.read_text())
    assert len(results) >= 4, "Esperadas ao menos quatro instâncias."
    by_case = {item["name"]: item for item in results}
    assert len(by_case) == len(results), "Nomes de instância duplicados."

    totals = {name: 0 for name in by_case}
    period_counts = {name: 0 for name in by_case}
    with measurements_path.open(newline="") as stream:
        for row in csv.DictReader(stream):
            name = row["case"]
            assert name in by_case, f"Instância desconhecida no CSV: {name}"
            ku, kv, count = int(row["ku"]), int(row["kv"]), int(row["count"])
            assert count > 0
            item = by_case[name]
            order = item["order"]
            assert 0 <= ku < order and 0 <= kv < order
            totals[name] += count
            if (kv - item["secret_d"] * ku) % order == 0:
                period_counts[name] += count

    for name, item in by_case.items():
        assert totals[name] == item["shots"], (
            f"{name}: CSV soma {totals[name]}, JSON declara {item['shots']} shots"
        )
        assert period_counts[name] == item["shots"], (
            f"{name}: nem todas as amostras satisfazem a relação de período"
        )
        assert item["recovered_d"] == item["secret_d"] and item["success"]
        assert item["logical_qubits"] == (
            2 * item["phase_qubits_each"] + item["point_qubits"]
        )
        print(
            f"{name}: {totals[name]} shots conferidos; "
            f"d={item['recovered_d']} recuperado; "
            f"{item['logical_qubits']} qubits abstratos"
        )

    # Validação do experimento em circuito Qiskit/Aer, gerado no mesmo workflow.
    qiskit_results = json.loads(qiskit_results_path.read_text())
    qiskit_by_case = {item["name"]: item for item in qiskit_results}
    assert len(qiskit_by_case) == 4, "Esperadas quatro instâncias Qiskit/Aer."
    qiskit_totals = {name: 0 for name in qiskit_by_case}
    with qiskit_measurements_path.open(newline="") as stream:
        for row in csv.DictReader(stream):
            name = row["case"]
            assert name in qiskit_by_case, f"Instância Qiskit desconhecida: {name}"
            count = int(row["count"])
            assert count > 0
            qiskit_totals[name] += count
    for name, item in qiskit_by_case.items():
        assert qiskit_totals[name] == item["shots"], f"{name}: shots Qiskit inconsistentes"
        assert item["success"] and item["recovered_d"] == item["secret_d"], (
            f"{name}: escalar não recuperado no circuito Qiskit/Aer"
        )
        assert item["transpiled_depth"] > 0
        assert item["transpiled_total_operations"] > 0
        assert item["transpiled_two_qubit_operations"] > 0
        assert item["period_relation_fraction"] > 0.4
        print(
            f"{name}: Qiskit/Aer recuperou d={item['recovered_d']}; "
            f"depth={item['transpiled_depth']}; "
            f"2Q={item['transpiled_two_qubit_operations']}"
        )

    print("Validação estrutural NumPy + Qiskit/Aer concluída.")


if __name__ == "__main__":
    main()
