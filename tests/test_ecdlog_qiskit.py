import unittest

from src.ecdlog_qiskit import CASES, build_ecdlog_circuit, run_case


class QiskitECDLPTests(unittest.TestCase):
    def test_builds_reversible_ecdlog_circuit(self):
        circuit, metadata = build_ecdlog_circuit(CASES[0], secret=3)
        self.assertEqual(circuit.num_qubits, 6)
        self.assertEqual(metadata["Q"], [1, 3])
        self.assertGreater(circuit.count_ops().get("mcx", 0), 0)

    def test_aer_recovers_reduced_secret_and_reports_metrics(self):
        result = run_case(CASES[0], secret=3, shots=512, seed=42)
        self.assertTrue(result["success"])
        self.assertEqual(result["recovered_d"], 3)
        self.assertEqual(result["shots"], 512)
        self.assertAlmostEqual(result["period_relation_fraction"], 1.0)
        self.assertGreater(result["transpiled_depth"], 0)
        self.assertGreater(result["transpiled_total_operations"], 0)
        self.assertGreater(result["transpiled_two_qubit_operations"], 0)


if __name__ == "__main__":
    unittest.main()
