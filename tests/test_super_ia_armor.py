"""
Unit tests for the SuperIAArmor core module in IDC.
Validates 2000 Energy management, Causal Pin Invariant Shields,
Hardware Entropy Harvester, and Colmena B3B Mesh resilience.
"""

import unittest
from core.super_ia_armor import SuperIAArmor


class TestSuperIAArmor(unittest.TestCase):

    def setUp(self):
        self.armor = SuperIAArmor(initial_energy=2000.0)

    def test_armor_energy_initialization(self):
        telemetry = self.armor.energy_mgr.telemetry()
        self.assertEqual(telemetry["energy"], 2000.0)
        self.assertEqual(telemetry["mode"], "EXPLORATION")
        self.assertEqual(telemetry["stress_factor"], 1.0)
        self.assertFalse(telemetry["is_depleted"])

    def test_pin_validation_normal_and_veto(self):
        # 1. Normal valid pin command
        res = self.armor.validate_pin_command(pin=13, value=1, command_type="OUTPUT")
        self.assertTrue(res["allowed"])
        self.assertEqual(self.armor.pin_states[13]["value"], 1)

        # 2. PWM out of bounds veto
        res_pwm = self.armor.validate_pin_command(pin=9, value=300, command_type="PWM")
        self.assertFalse(res_pwm["allowed"])
        self.assertEqual(res_pwm["veto_code"], "CAUSAL_VETO_PWM_BOUNDS")

        # 3. E-STOP active blocks power actuators
        self.armor.set_estop(True)
        res_estop = self.armor.validate_pin_command(pin=9, value=128, command_type="PWM")
        self.assertFalse(res_estop["allowed"])
        self.assertEqual(res_estop["veto_code"], "CAUSAL_VETO_ESTOP")

    def test_hardware_entropy_harvesting(self):
        entropy = self.armor.harvest_hardware_entropy()
        self.assertIn("entropy_value", entropy)
        self.assertIn("jitter_nanoseconds", entropy)
        self.assertIn("seed_hex", entropy)
        self.assertEqual(entropy["token_cost"], 0)
        self.assertLess(self.armor.energy_mgr.available(), 2000.0)

    def test_colmena_mesh_routing_and_resilience(self):
        # 1. Direct route when nodes are online
        ping_res = self.armor.colmena_ping_mesh("IDC_BRAIN", "BUNKKER_BOX")
        self.assertTrue(ping_res["success"])
        self.assertEqual(ping_res["status"], "ENRUTAMIENTO_DIRECTO")

        # 2. Simulate node crash (BUNKKER_BOX offline)
        toggle = self.armor.toggle_node_status("BUNKKER_BOX")
        self.assertTrue(toggle["success"])
        self.assertEqual(toggle["new_status"], "OFFLINE")

        # 3. Reroute via surviving mesh peer
        ping_reroute = self.armor.colmena_ping_mesh("IDC_BRAIN", "BUNKKER_BOX")
        self.assertTrue(ping_reroute["success"])
        self.assertEqual(ping_reroute["status"], "DESVIADO_POR_FALLO_DE_NODO")
        self.assertTrue(ping_reroute["is_resilient"])

    def test_self_audit(self):
        audit = self.armor.run_self_audit()
        self.assertIn("energy", audit)
        self.assertIn("causal_invariants_checked", audit)
        self.assertIn("colmena_health", audit)
        self.assertEqual(audit["hardware_safety"], "PROTEGIDO_POR_ESCUDO")


if __name__ == "__main__":
    unittest.main()
