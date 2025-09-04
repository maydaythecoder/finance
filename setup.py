#!/usr/bin/env python3
"""
Setup and validation script for Fake Trading Price Simulator

SECURITY: Validates environment and dependencies
SAFETY: Ensures all required files and permissions are correct
"""

import sys
import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any


def check_python_version() -> bool:
    """Check if Python version meets requirements."""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def check_required_modules() -> bool:
    """Check if all required modules are available."""
    required_modules = [
        'json', 'time', 'random', 'logging', 
        'datetime', 'pathlib', 'sys', 'typing'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing required modules: {missing_modules}")
        return False
    
    print("✅ All required modules available")
    return True


def validate_data_file() -> bool:
    """Validate the data.json file structure and content."""
    data_file = Path("data.json")
    
    if not data_file.exists():
        print("❌ data.json file not found")
        return False
    
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        # Check required keys
        required_keys = {"open", "high", "low", "close"}
        if not required_keys.issubset(data.keys()):
            missing = required_keys - data.keys()
            print(f"❌ Missing required keys in data.json: {missing}")
            return False
        
        # Check numeric types
        for key in required_keys:
            if not isinstance(data[key], (int, float)):
                print(f"❌ Value for '{key}' must be numeric, got {type(data[key])}")
                return False
        
        # Check logical constraints
        if data["high"] < data["low"]:
            print(f"❌ High price ({data['high']}) cannot be less than low price ({data['low']})")
            return False
        
        if data["open"] < data["low"] or data["open"] > data["high"]:
            print(f"❌ Open price ({data['open']}) must be within low-high range")
            return False
        
        if data["close"] < data["low"] or data["close"] > data["high"]:
            print(f"❌ Close price ({data['close']}) must be within low-high range")
            return False
        
        print("✅ data.json validation passed")
        print(f"   Market data: Open=${data['open']:.2f}, High=${data['high']:.2f}, Low=${data['low']:.2f}, Close=${data['close']:.2f}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format in data.json: {e}")
        return False
    except Exception as e:
        print(f"❌ Error validating data.json: {e}")
        return False


def check_main_script() -> bool:
    """Check if the main script exists and is executable."""
    script_file = Path("faketrading.py")
    
    if not script_file.exists():
        print("❌ faketrading.py not found")
        return False
    
    # Check if file is readable
    if not os.access(script_file, os.R_OK):
        print("❌ faketrading.py is not readable")
        return False
    
    # Try to make executable on Unix-like systems
    if os.name != 'nt':  # Not Windows
        try:
            os.chmod(script_file, 0o755)
            print("✅ Made faketrading.py executable")
        except Exception as e:
            print(f"⚠️  Could not make faketrading.py executable: {e}")
    
    print("✅ faketrading.py found and ready")
    return True


def check_test_suite() -> bool:
    """Check if test suite is available."""
    test_file = Path("test_faketrading.py")
    
    if not test_file.exists():
        print("⚠️  test_faketrading.py not found (tests will not be available)")
        return True  # Not critical for basic setup
    
    print("✅ Test suite available")
    return True


def check_makefile() -> bool:
    """Check if Makefile is available."""
    makefile = Path("Makefile")
    
    if not makefile.exists():
        print("⚠️  Makefile not found (make commands will not be available)")
        return True  # Not critical for basic setup
    
    print("✅ Makefile available")
    return True


def run_quick_test() -> bool:
    """Run a quick test to ensure the simulator works."""
    try:
        # Import the simulator
        from faketrading import PriceSimulator
        
        # Create simulator instance
        simulator = PriceSimulator()
        
        # Load market data
        market_data = simulator.load_market_data()
        
        # Test price generation
        simulator.market_data = market_data
        simulator.current_price = market_data["open"]
        
        # Generate a few test prices
        for i in range(1, 5):
            price = simulator.generate_price(i)
            if not (market_data["low"] <= price <= market_data["high"]):
                print(f"❌ Generated price {price} outside bounds")
                return False
        
        print("✅ Quick functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ Quick functionality test failed: {e}")
        return False


def create_output_directory() -> bool:
    """Create output directory if it doesn't exist."""
    output_dir = Path("output")
    
    if not output_dir.exists():
        try:
            output_dir.mkdir()
            print("✅ Created output directory")
        except Exception as e:
            print(f"⚠️  Could not create output directory: {e}")
            return True  # Not critical
    
    return True


def check_permissions() -> bool:
    """Check file permissions."""
    files_to_check = ["faketrading.py", "data.json"]
    
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            if not os.access(path, os.R_OK):
                print(f"❌ {file_path} is not readable")
                return False
    
    print("✅ File permissions are correct")
    return True


def print_summary() -> None:
    """Print setup summary and next steps."""
    print("\n" + "="*50)
    print("SETUP SUMMARY")
    print("="*50)
    print("✅ Environment validation complete")
    print("\nNext steps:")
    print("1. Run the simulator: python faketrading.py")
    print("2. Run tests: python test_faketrading.py")
    print("3. Use make commands: make help")
    print("\nFor more information, see:")
    print("- README.MD (full documentation)")
    print("- QUICKSTART.md (quick start guide)")
    print("="*50)


def main() -> int:
    """Main setup function."""
    print("🔧 Fake Trading Price Simulator Setup")
    print("="*50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Modules", check_required_modules),
        ("Data File", validate_data_file),
        ("Main Script", check_main_script),
        ("Test Suite", check_test_suite),
        ("Makefile", check_makefile),
        ("File Permissions", check_permissions),
        ("Output Directory", create_output_directory),
        ("Quick Test", run_quick_test),
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}...")
        if not check_func():
            all_passed = False
    
    if all_passed:
        print_summary()
        return 0
    else:
        print("\n❌ Setup failed. Please fix the issues above and run setup again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
