"""
Automated Unit Tests for Food Rescue Machine Learning System
Run with:
    python3 -m unittest tests/test_ml_app.py
"""

import unittest
import os
from ml_engine import ml_system, load_dataset, encode_row

class TestFoodRescueML(unittest.TestCase):
    def test_01_dataset_loading(self):
        X, y, records = load_dataset()
        self.assertGreaterEqual(len(X), 1000)
        self.assertEqual(len(X), len(y))
        self.assertEqual(len(X[0]), 18)

    def test_02_model_prediction(self):
        test_input = {
            'category': 'cooked_meals',
            'food_type': 'veg',
            'ambient_temp_c': 32.0,
            'humidity_percent': 65.0,
            'storage_condition': 'ambient_room',
            'packaging_type': 'plastic_wrap',
            'prepared_hours_ago': 2.0
        }
        res = ml_system.predict(test_input)
        self.assertIn('predicted_hours', res)
        self.assertGreaterEqual(res['predicted_hours'], 0.0)
        self.assertIn('urgency_tier', res)
        self.assertIn(res['urgency_tier'], ['NORMAL', 'HIGH_PRIORITY', 'RED_ALERT', 'CRITICAL_EXPIRED'])
        self.assertIn('decay_curve', res)
        self.assertGreater(len(res['decay_curve']), 3)

    def test_03_refrigeration_effect(self):
        ambient_res = ml_system.predict({
            'category': 'dairy',
            'ambient_temp_c': 30.0,
            'storage_condition': 'ambient_room',
            'prepared_hours_ago': 1.0
        })
        refrig_res = ml_system.predict({
            'category': 'dairy',
            'ambient_temp_c': 30.0,
            'storage_condition': 'refrigerated',
            'prepared_hours_ago': 1.0
        })
        self.assertGreater(refrig_res['predicted_hours'], ambient_res['predicted_hours'])

    def test_04_model_accuracy_metrics(self):
        self.assertGreaterEqual(ml_system.metrics['r2_score'], 0.85)
        self.assertLessEqual(ml_system.metrics['rmse'], 25.0)

    def test_05_model_comparisons(self):
        models = ml_system.comparison_models
        self.assertIn('Random Forest Regressor', models)
        self.assertIn('Gradient Boosting Regressor', models)
        self.assertIn('Decision Tree Regressor', models)
        self.assertGreater(models['Random Forest Regressor']['r2'], models['Decision Tree Regressor']['r2'])

    def test_06_sms_otp_generation_and_verification(self):
        import sms_service
        phone = "9876543210"
        clean_phone, otp = sms_service.generate_otp(phone)
        self.assertEqual(clean_phone, "9876543210")
        self.assertEqual(len(otp), 4)
        self.assertTrue(otp.isdigit())

        # Test valid verification
        valid, msg = sms_service.verify_otp(phone, otp)
        self.assertTrue(valid)

    def test_07_invalid_otp_rejection(self):
        import sms_service
        phone = "9123456789"
        clean_phone, otp = sms_service.generate_otp(phone)
        valid, msg = sms_service.verify_otp(phone, "0000" if otp != "0000" else "9999")
        self.assertFalse(valid)
        self.assertIn("Incorrect", msg)

if __name__ == '__main__':
    unittest.main()
