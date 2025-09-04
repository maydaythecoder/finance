# Fake Trading Price Simulator - Quick Start Guide

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.7 or higher
- No external dependencies required

### 2. Setup

```bash
# Run the setup script to validate everything
python setup.py

# Or manually check requirements
python -c "import sys; assert sys.version_info >= (3, 7), 'Python 3.7+ required'"
```

### 3. Run the Simulator

```bash
# Basic run
python faketrading.py

# With custom volatility (if modified)
python faketrading.py
```

## 📊 Expected Output

The simulator will output real-time price updates:

``` txt
[2023-10-05 09:30:00] [1_SECOND] Price: $154.12
[2023-10-05 09:30:05] [5_SECOND] Price: $154.45
[2023-10-05 09:31:00] [1_MINUTE] Price: $154.71
```

And generate a `simulation_results.json` file with complete data.

## 🧪 Testing

```bash
# Run all tests
python test_faketrading.py

# Or use make
make test
```

## 🔧 Configuration

The simulator uses these default settings:

- **Volatility**: 0.5 (moderate price movement)
- **Duration**: 60 seconds
- **Data file**: data.json
- **Output**: simulation_results.json

## 📁 File Structure

``` txt
finance/
├── faketrading.py          # Main simulator
├── data.json               # Market data input
├── test_faketrading.py     # Test suite
├── setup.py                # Setup script
├── Makefile                # Development tasks
├── requirements.txt        # Dependencies
├── config_template.py      # Configuration template
├── .gitignore             # Git ignore rules
└── README.MD              # Full documentation
```

## 🔒 Security Notes

- All inputs are validated for security
- File paths are sanitized to prevent traversal attacks
- JSON data is validated for structure and constraints
- Price bounds are enforced throughout simulation

## ⚠️ Important Notes

- This is a **simulation tool**, not real trading software
- Generated data is for testing and educational purposes only
- Do not use for actual trading decisions
- The simulator converges to the exact close price after 60 seconds

## 🆘 Troubleshooting

### Common Issues

### **"Market data file not found"**

- Ensure `data.json` exists in the project directory
- Run `python setup.py` to validate

### **"High price cannot be less than low price"**

- Check `data.json` format
- Ensure high ≥ low, open/close within range

### **Permission errors**

- Run `python setup.py` to set correct permissions
- Ensure Python executable permissions

### Getting Help

1. Check the full README.MD for detailed documentation
2. Run `make help` for available commands
3. Review test output for specific error details
4. Validate data with `python setup.py`

---

## *For full documentation, see README.MD*
