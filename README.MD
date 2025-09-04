# Fake Trading Price Simulator

A sophisticated Python-based trading price simulator that generates realistic market price movements with guaranteed convergence to target closing prices. Built with security-first principles and production-ready error handling.

## 🎯 Overview

This simulator creates realistic price movements within defined market bounds, converging precisely on a known closing price after 60 seconds. It's designed for:

- **Testing trading algorithms** with realistic price data
- **Backtesting strategies** with controlled market conditions
- **Educational purposes** for understanding price dynamics
- **Development environments** requiring consistent test data

## 🔒 Security Features

### **SECURITY: Input validation prevents malformed JSON exploitation**

- Validates all JSON structure and data types
- Enforces market logic constraints (high ≥ low, open/close within bounds)
- Sanitizes filenames to prevent path traversal attacks
- Uses allow-list validation for interval types

### **SAFETY: Price bounds enforcement prevents unrealistic market conditions**

- Enforces price bounds throughout simulation
- Implements convergence algorithm with controlled randomness
- Uses normal distribution to prevent extreme outliers
- Provides precise timing control for consistent intervals

## 🏗️ Architecture

``` txt
finance/
├── faketrading.py          # Main simulator engine
├── data.json               # Market data input
├── test_faketrading.py     # Comprehensive test suite
├── setup.py                # Setup and validation script
├── Makefile                # Development automation
├── requirements.txt        # Dependencies (standard library only)
├── config.py               # Configuration management
├── config_template.py      # Configuration template
├── QUICKSTART.md           # Quick start guide
├── architecture.mmd        # Architecture diagram source
├── architecture.svg        # Architecture visualization
├── output/                 # Output directory
├── simulation_results.json # Generated simulation data
└── README.MD              # This documentation
```

### Core Components

``` txt
faketrading.py          # Main simulator engine
├── PriceSimulator      # Core simulation class
├── load_market_data()  # JSON validation & loading
├── generate_price()    # Convergence algorithm
├── run_simulation()    # 60-second execution loop
└── export_results()    # Structured output
```

## 📊 Data Format

### Input (`data.json`)

```json
{
  "open": 154.12,
  "high": 154.89,
  "low": 153.95,
  "close": 154.71
}
```

### Output (`simulation_results.json`)

```json
{
  "simulation_metadata": {
    "volatility": 0.5,
    "data_file": "data.json",
    "market_data": {...},
    "total_records": 60
  },
  "price_data": [
    {
      "timestamp": "2023-10-05 09:30:00",
      "interval": "1_SECOND",
      "price": 154.12
    }
  ]
}
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- No external dependencies (uses standard library only)

### Installation

```bash
# Clone or download the project
git clone <repository-url>
cd finance

# Run setup validation
python setup.py

# Or use make for quick validation
make validate
```

### Running the Simulator

```bash
# Basic run
python faketrading.py

# Using make
make run

# With custom configuration
python faketrading.py
```

### Configuration

```python
# In faketrading.py main() function
volatility = 0.5        # Controls price movement randomness
data_file = "data.json"  # Market data source
```

## 📈 Usage Examples

### Basic Simulation

```bash
python faketrading.py
```

### Custom Configuration

```python
from faketrading import PriceSimulator

# Create simulator with custom parameters
simulator = PriceSimulator(
    volatility=0.3,      # Lower volatility
    data_file="custom_data.json"
)

# Run simulation
results = simulator.run_simulation()

# Export results
simulator.export_results("custom_results.json")
```

### Real-time Output

The simulator provides real-time console output:

``` txt
[2023-10-05 09:30:00] [1_SECOND] Price: $154.12
[2023-10-05 09:30:05] [5_SECOND] Price: $154.45
[2023-10-05 09:31:00] [1_MINUTE] Price: $154.71
```

## 🧪 Testing & Development

### Running Tests

```bash
# Run all tests
python test_faketrading.py

# Using make
make test

# With coverage
make test-cov
```

### Code Quality

```bash
# Lint code
make lint

# Format code
make format

# Type checking
make typecheck

# Security checks
make security
```

### Development Setup

```bash
# Install development dependencies
make install-dev

# Validate everything
make validate
```

## 🔧 Technical Details

### Convergence Algorithm

The simulator uses a weighted convergence approach:

1. **Convergence Weight**: Increases over time (0 → 0.9)
2. **Target Bias**: Stronger bias toward close price as simulation progresses
3. **Random Component**: Normal distribution with decreasing volatility
4. **Bounds Enforcement**: Ensures prices stay within high/low range

### Timing Control

- **Precise 1-second intervals** using `time.sleep()`
- **Synchronized timestamps** for consistent data
- **Graceful interruption** handling with `KeyboardInterrupt`

### Logging Intervals

- `1_SECOND`: Every second
- `5_SECOND`: Every 5 seconds
- `1_MINUTE`: At minute end
- `5_MINUTE`: At start (for 1-minute simulations)
- `1_HOUR`: At start (for 1-minute simulations)

## 🧪 Testing

### Validation Tests

```python
# Test market data validation
def test_market_data_validation():
    # Test high < low constraint
    # Test open/close within bounds
    # Test required keys presence
    pass

# Test convergence algorithm
def test_price_convergence():
    # Verify final price equals target close
    # Check price bounds throughout simulation
    pass
```

### Security Tests

```python
# Test JSON injection prevention
def test_json_injection():
    # Test malformed JSON handling
    # Test missing required keys
    pass

# Test path traversal prevention
def test_filename_sanitization():
    # Test ../ path traversal attempts
    # Test absolute path handling
    pass
```

## 📋 Requirements

### System Requirements

- **OS**: Cross-platform (Windows, macOS, Linux)
- **Python**: 3.7 or higher
- **Memory**: Minimal (< 10MB)
- **Storage**: < 1MB for code and data

### Dependencies

- `json` - JSON parsing and validation
- `time` - Timing control and sleep
- `random` - Price movement generation
- `logging` - Structured logging
- `datetime` - Timestamp management
- `pathlib` - File path handling
- `sys` - System exit handling

### Development Dependencies (Optional)

- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking

## 🔍 Troubleshooting

### Common Issues

### **FileNotFoundError: Market data file not found**

```bash
# Ensure data.json exists in project directory
ls -la data.json

# Run setup validation
python setup.py
```

### **ValueError: High price cannot be less than low price**

```json
// Fix data.json structure
{
  "open": 154.12,
  "high": 154.89,  // Must be >= low
  "low": 153.95,
  "close": 154.71  // Must be within high-low range
}
```

### **Simulation timing issues**

- Check system clock accuracy
- Ensure no heavy background processes
- Verify Python version compatibility

### Debug Mode

```python
# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 API Reference

### PriceSimulator Class

#### Constructor

```python
PriceSimulator(volatility: float = 0.5, data_file: str = "data.json")
```

#### Methods

- `load_market_data() -> Dict[str, float]`: Load and validate market data
- `generate_price(second: int, total_seconds: int = 60) -> float`: Generate next price
- `run_simulation() -> List[Dict[str, Any]]`: Execute 60-second simulation
- `export_results(filename: str = "simulation_results.json") -> None`: Export results

## 🤝 Contributing

### Security Guidelines

1. **Input Validation**: Always validate external inputs
2. **Bounds Checking**: Enforce logical constraints
3. **Error Handling**: Provide meaningful error messages
4. **Logging**: Use structured logging for debugging

### Code Style

- Follow PEP 8 conventions
- Include type hints
- Add security annotations (`SECURITY:`, `SAFETY:`)
- Document all public methods

### Development Workflow

```bash
# 1. Make changes
# 2. Run tests
make test

# 3. Check code quality
make lint
make typecheck

# 4. Format code
make format

# 5. Validate everything
make validate
```

## 📄 License

This project is provided as-is for educational and development purposes. Use at your own risk in production environments.

## ⚠️ Disclaimer

**This is a simulation tool, not real trading software.** The generated data is for testing and educational purposes only. Do not use for actual trading decisions.

## 📖 Additional Documentation

- [Quick Start Guide](QUICKSTART.md) - Get up and running quickly
- [Architecture Diagram](architecture.svg) - Visual system overview
- [Test Suite](test_faketrading.py) - Comprehensive test coverage
- [Configuration](config.py) - Configuration management

---

*Built with security-first principles and production-ready error handling.*
