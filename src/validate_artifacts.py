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
        assert item["period_relation_fraction"] == 1.0
        assert item["probability_correct_single_shot"] > 0.4
        assert item["total_experiment_seconds"] > 0
        print(
            f"{name}: Qiskit/Aer recuperou d={item['recovered_d']}; "
            f"depth={item['transpiled_depth']}; "
            f"2Q={item['transpiled_two_qubit_operations']}"
        )

    # Benchmark PQC: amostras brutas por operação, segredos coincidentes e recursos.
    benchmark = json.loads((ROOT / "data/benchmark_pqc.json").read_text())
    x_result = benchmark["x25519"]
    assert x_result["available"]
    assert len(x_result["raw_measurements_ms"]["keygen_pair"]) == x_result["repetitions"]
    assert len(x_result["raw_measurements_ms"]["two_exchanges"]) == x_result["repetitions"]
    ml_result = benchmark["ml_kem_768"]
    assert ml_result["available"], ml_result.get("reason", "ML-KEM indisponível")
    assert ml_result["secret_match"]
    for operation in ("keygen", "encaps", "decaps"):
        assert len(ml_result["raw_measurements_ms"][operation]) == ml_result["repetitions"]
    assert "resource_usage" in benchmark
    print("Benchmark X25519/ML-KEM: amostras brutas, igualdade de segredos e recursos conferidos.")

    # Cenário quantitativo definido no enunciado: uma chave pública X25519 (32 B)
    # versus um ciphertext ML-KEM-768 (1.088 B) por estabelecimento.
    with (ROOT / "data/communication_scenario.csv").open(newline="") as stream:
        communication = next(csv.DictReader(stream))
    assert int(communication["sessions"]) == 1_000_000
    assert int(communication["x25519_bytes"]) == 32_000_000
    assert int(communication["ml_kem_768_bytes"]) == 1_088_000_000
    assert int(communication["additional_bytes"]) == 1_056_000_000
    print("Cenário de comunicação 1 milhão: acréscimo de 1.056.000.000 bytes conferido.")

    with (ROOT / "data/storage_scenario.csv").open(newline="") as stream:
        storage_rows = list(csv.DictReader(stream))
    storage = {row["element"]: row for row in storage_rows}
    assert int(storage["public_keys"]["additional_bytes"]) == 1_152_000_000
    assert int(storage["private_keys_raw"]["additional_bytes"]) == 2_368_000_000
    print("Cenário de armazenamento para 1 milhão de chaves públicas/privadas conferido.")

    print("Validação estrutural completa concluída.")


if __name__ == "__main__":
    main()
