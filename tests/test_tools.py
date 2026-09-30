import unittest

from agent.tools import calculator, cvss_severity, policy_lookup


class ToolTests(unittest.TestCase):
    def test_calculator(self):
        self.assertEqual(calculator("12.5 * 8"), 100)
        self.assertEqual(calculator("(15 + 5) * 3"), 60)

    def test_calculator_rejects_code(self):
        with self.assertRaises(Exception):
            calculator("__import__('os').system('ls')")

    def test_cvss_boundaries(self):
        cases = {0.0: "None", 0.1: "Low", 3.9: "Low", 4.0: "Medium", 6.9: "Medium",
                 7.0: "High", 8.9: "High", 9.0: "Critical", 10.0: "Critical"}
        for score, sev in cases.items():
            self.assertEqual(cvss_severity(score), sev)

    def test_cvss_out_of_range(self):
        with self.assertRaises(ValueError):
            cvss_severity(10.1)

    def test_policy(self):
        self.assertEqual(policy_lookup("Critical"), 3)
        with self.assertRaises(KeyError):
            policy_lookup("None")


if __name__ == "__main__":
    unittest.main()
