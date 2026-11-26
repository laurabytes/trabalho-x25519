import shutil
import unittest

from src.benchmark_pqc import benchmark_ml_kem, benchmark_x25519, run


class PQCBenchmarkTests(unittest.TestCase):
    def test_x25519_derives_matching_secrets(self):
        result = benchmark_x25519(2)
        self.assertTrue(result["available"])
        self.assertEqual(result["public_key_bytes"], 32)
        self.assertEqual(result["shared_secret_bytes"], 32)
        self.assertEqual(len(result["raw_measurements_ms"]["keygen_pair"]), 2)
        self.assertEqual(len(result["raw_measurements_ms"]["two_exchanges"]), 2)

    def test_ml_kem_round_trip(self):
        openssl = shutil.which("openssl")
        if not openssl:
            self.skipTest("openssl não está instalado")
        algorithms = run([openssl, "list", "-kem-algorithms"]).stdout.lower()
        if "ml-kem-768" not in algorithms:
            self.skipTest("esta instalação do openssl não oferece ml-kem-768")
        result = benchmark_ml_kem(1, openssl)
        self.assertTrue(result["secret_match"])
        self.assertEqual(result["ciphertext_bytes"], 1088)
        self.assertEqual(result["shared_secret_bytes"], 32)
        self.assertEqual(len(result["raw_measurements_ms"]["keygen"]), 1)
        self.assertEqual(len(result["raw_measurements_ms"]["encaps"]), 1)
        self.assertEqual(len(result["raw_measurements_ms"]["decaps"]), 1)


if __name__ == "__main__":
    unittest.main()
