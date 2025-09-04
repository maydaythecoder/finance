#!/usr/bin/env python3
"""
Test suite for Fake Trading Price Simulator

SECURITY: Tests input validation and security measures
SAFETY: Validates convergence algorithm and bounds enforcement
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from faketrading import PriceSimulator


class TestPriceSimulator(unittest.TestCase):
    """Test cases for PriceSimulator class"""

    def setUp(self):
        """Set up test fixtures"""
        self.valid_market_data = {
            "open": 154.12,
            "high": 154.89,
            "low": 153.95,
            "close": 154.71
        }
        
    def test_valid_market_data_loading(self):
        """Test loading valid market data"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.valid_market_data, f)
            temp_file = f.name
            
        try:
            simulator = PriceSimulator(data_file=temp_file)
            loaded_data = simulator.load_market_data()
            
            self.assertEqual(loaded_data["open"], 154.12)
            self.assertEqual(loaded_data["high"], 154.89)
            self.assertEqual(loaded_data["low"], 153.95)
            self.assertEqual(loaded_data["close"], 154.71)
        finally:
            Path(temp_file).unlink()
            
    def test_invalid_json_format(self):
        """Test handling of malformed JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"open": 154.12, "high": 154.89, "low": 153.95, "close": 154.71')  # Missing closing brace
            temp_file = f.name
            
        try:
            simulator = PriceSimulator(data_file=temp_file)
            with self.assertRaises(ValueError):
                simulator.load_market_data()
        finally:
            Path(temp_file).unlink()
            
    def test_missing_required_keys(self):
        """Test validation of required market data keys"""
        invalid_data = {"open": 154.12, "high": 154.89}  # Missing low and close
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_data, f)
            temp_file = f.name
            
        try:
            simulator = PriceSimulator(data_file=temp_file)
            with self.assertRaises(ValueError) as context:
                simulator.load_market_data()
            self.assertIn("Missing required keys", str(context.exception))
        finally:
            Path(temp_file).unlink()
            
    def test_invalid_price_constraints(self):
        """Test validation of price logic constraints"""
        invalid_data = {
            "open": 154.12,
            "high": 153.95,  # High < Low
            "low": 154.89,
            "close": 154.71
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_data, f)
            temp_file = f.name
            
        try:
            simulator = PriceSimulator(data_file=temp_file)
            with self.assertRaises(ValueError) as context:
                simulator.load_market_data()
            self.assertIn("High price", str(context.exception))
        finally:
            Path(temp_file).unlink()
            
    def test_open_price_out_of_bounds(self):
        """Test validation of open price within high-low range"""
        invalid_data = {
            "open": 160.00,  # Above high
            "high": 154.89,
            "low": 153.95,
            "close": 154.71
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_data, f)
            temp_file = f.name
            
        try:
            simulator = PriceSimulator(data_file=temp_file)
            with self.assertRaises(ValueError) as context:
                simulator.load_market_data()
            self.assertIn("Open price", str(context.exception))
        finally:
            Path(temp_file).unlink()
            
    def test_close_price_out_of_bounds(self):
        """Test validation of close price within high-low range"""
        invalid_data = {
            "open": 154.12,
            "high": 154.89,
            "low": 153.95,
            "close": 160.00  # Above high
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_data, f)
            temp_file = f.name
            
        try:
            simulator = PriceSimulator(data_file=temp_file)
            with self.assertRaises(ValueError) as context:
                simulator.load_market_data()
            self.assertIn("Close price", str(context.exception))
        finally:
            Path(temp_file).unlink()
            
    def test_price_generation_bounds(self):
        """Test that generated prices stay within bounds"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.valid_market_data, f)
            temp_file = f.name
            
        try:
            simulator = PriceSimulator(data_file=temp_file, volatility=0.1)
            simulator.market_data = simulator.load_market_data()
            simulator.current_price = simulator.market_data["open"]
            
            # Test multiple price generations
            for second in range(1, 60):
                new_price = simulator.generate_price(second)
                self.assertGreaterEqual(new_price, simulator.market_data["low"])
                self.assertLessEqual(new_price, simulator.market_data["high"])
        finally:
            Path(temp_file).unlink()
            
    def test_convergence_to_target(self):
        """Test that final price converges to target close price"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.valid_market_data, f)
            temp_file = f.name
            
        try:
            simulator = PriceSimulator(data_file=temp_file, volatility=0.1)
            simulator.market_data = simulator.load_market_data()
            simulator.current_price = simulator.market_data["open"]
            
            # Run full simulation
            results = simulator.run_simulation()
            
            # Check final price equals target close
            final_price = simulator.current_price
            target_close = simulator.market_data["close"]
            self.assertAlmostEqual(final_price, target_close, places=2)
        finally:
            Path(temp_file).unlink()
            
    def test_filename_sanitization(self):
        """Test path traversal prevention in filename sanitization"""
        simulator = PriceSimulator()
        
        # Test path traversal attempts
        malicious_filenames = [
            "../../../etc/passwd",
            "/absolute/path/file.json",
            "file.json/../malicious"
        ]
        
        for malicious_name in malicious_filenames:
            with self.assertRaises(Exception):
                simulator.export_results(malicious_name)
                
    def test_interval_validation(self):
        """Test interval type validation"""
        simulator = PriceSimulator()
        
        # Test valid intervals
        valid_intervals = ["1_SECOND", "5_SECOND", "1_MINUTE", "5_MINUTE", "1_HOUR"]
        for interval in valid_intervals:
            # Should not raise exception
            simulator.log_price(interval, 154.12)
            
        # Test invalid interval
        with self.assertRaises(Exception):
            simulator.log_price("INVALID_INTERVAL", 154.12)
            
    @patch('time.sleep')
    def test_simulation_timing(self, mock_sleep):
        """Test simulation timing control"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.valid_market_data, f)
            temp_file = f.name
            
        try:
            simulator = PriceSimulator(data_file=temp_file)
            results = simulator.run_simulation()
            
            # Verify sleep was called for timing control
            self.assertTrue(mock_sleep.called)
            
            # Verify we got expected number of results
            self.assertGreater(len(results), 0)
        finally:
            Path(temp_file).unlink()


class TestSecurityMeasures(unittest.TestCase):
    """Test security-specific functionality"""
    
    def test_json_injection_prevention(self):
        """Test prevention of JSON injection attacks"""
        # Test with malformed JSON that could cause issues
        malformed_json = '{"open": 154.12, "high": 154.89, "low": 153.95, "close": 154.71, "malicious": "<script>alert(1)</script>"}'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(malformed_json)
            temp_file = f.name
            
        try:
            simulator = PriceSimulator(data_file=temp_file)
            # Should only load required keys, ignore malicious content
            data = simulator.load_market_data()
            self.assertNotIn("malicious", data)
        finally:
            Path(temp_file).unlink()
            
    def test_numeric_type_validation(self):
        """Test validation of numeric data types"""
        invalid_data = {
            "open": "154.12",  # String instead of number
            "high": 154.89,
            "low": 153.95,
            "close": 154.71
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_data, f)
            temp_file = f.name
            
        try:
            simulator = PriceSimulator(data_file=temp_file)
            with self.assertRaises(ValueError) as context:
                simulator.load_market_data()
            self.assertIn("must be numeric", str(context.exception))
        finally:
            Path(temp_file).unlink()


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
