import unittest

from src.ecdlog_shor import CASES, point_add, point_mul, point_order, run_case


class ECDLPTests(unittest.TestCase):
    def test_curve_orders_and_public_points(self):
        for case in CASES:
            with self.subTest(case=case["name"]):
                self.assertEqual(
                    point_order(case["P"], case["a"], case["p"]),
                    case["r"],
                )
                self.assertEqual(
                    point_mul(3, case["P"], case["a"], case["p"]),
                    {
                        "C4_F5": (1, 3),
                        "C8_F5": (1, 4),
                        "C16_F11": (8, 1),
                        "C32_F23": (8, 22),
                    }[case["name"]],
                )

    def test_inverse_points_sum_to_identity(self):
        case = CASES[-1]
        P = case["P"]
        inverse = (P[0], (-P[1]) % case["p"])
        self.assertIsNone(point_add(P, inverse, case["a"], case["p"]))

    def test_shor_structure_recovers_test_scalar(self):
        for index, case in enumerate(CASES):
            with self.subTest(case=case["name"]):
                result = run_case(case, secret=3, shots=4096, seed=20261110 + index)
                self.assertTrue(result["success"])
                self.assertEqual(result["recovered_d"], 3)
                self.assertAlmostEqual(result["period_relation_fraction"], 1.0)


if __name__ == "__main__":
    unittest.main()
