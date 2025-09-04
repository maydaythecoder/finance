# Fake Trading Price Simulator - API Documentation

## Overview

The Fake Trading Price Simulator provides a comprehensive API for generating realistic price movements with guaranteed convergence to target closing prices. This document details all public interfaces, configuration options, and usage patterns.

## Core Classes

### PriceSimulator

The main simulation engine that generates price movements and manages the simulation lifecycle.

#### Constructor

```python
PriceSimulator(volatility: float = 0.5, data_file: str = "data.json")
```

**Parameters:**

- `volatility` (float): Controls price movement randomness (0.0 = no movement, 2.0 = high volatility)
- `data_file` (str): Path to JSON file containing market data

**SECURITY:** Validates file path to prevent path traversal attacks

#### Methods

##### `load_market_data() -> Dict[str, float]`

Loads and validates market data from the specified JSON file.

**Returns:**

- `Dict[str, float]`: Validated market data with keys: `open`, `high`, `low`, `close`

**Raises:**

- `FileNotFoundError`: If data file doesn't exist
- `ValueError`: If JSON is malformed or validation fails
- `KeyError`: If required keys are missing

**SECURITY:** Validates JSON structure and enforces market logic constraints

**Example:**

```python
simulator = PriceSimulator()
market_data = simulator.load_market_data()
print(f"Open: ${market_data['open']:.2f}")
```

##### `generate_price(second: int, total_seconds: int = 60) -> float`

Generates the next price using controlled random walk with convergence bias.

**Parameters:**

- `second` (int): Current second in simulation (1-60)
- `total_seconds` (int): Total simulation duration (default: 60)

**Returns:**

- `float`: Generated price within market bounds

**SAFETY:** Ensures price stays within high/low bounds and converges to target close

**Algorithm:**

1. Calculate convergence weight (increases over time)
2. Apply target bias toward close price
3. Add random component with decreasing volatility
4. Enforce market bounds

**Example:**

```python
simulator = PriceSimulator()
simulator.market_data = simulator.load_market_data()
simulator.current_price = simulator.market_data["open"]

for second in range(1, 61):
    price = simulator.generate_price(second)
    print(f"Second {second}: ${price:.2f}")
```

##### `run_simulation() -> List[Dict[str, Any]]`

Executes the complete 60-second price simulation with multi-interval logging.

**Returns:**

- `List[Dict[str, Any]]`: List of price records with timestamps and intervals

**SAFETY:** Implements precise timing control and guaranteed convergence

**Features:**

- Real-time console output
- Multi-interval logging (1s, 5s, 1min)
- Precise 1-second timing
- Graceful interruption handling

**Example:**

```python
simulator = PriceSimulator()
results = simulator.run_simulation()
print(f"Generated {len(results)} price records")
```

##### `export_results(filename: str = "simulation_results.json") -> None`

Exports simulation results to JSON file with metadata.

**Parameters:**

- `filename` (str): Output file path

**SECURITY:** Sanitizes filename to prevent path traversal attacks

**Output Format:**

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

**Example:**

```python
simulator = PriceSimulator()
simulator.run_simulation()
simulator.export_results("my_results.json")
```

##### `log_price(interval: str, price: float, timestamp: datetime = None) -> None`

Logs price data with structured format.

**Parameters:**

- `interval` (str): Logging interval type
- `price` (float): Price value
- `timestamp` (datetime): Optional timestamp (defaults to current time)

**SECURITY:** Sanitizes interval string using allow-list validation

**Valid Intervals:**

- `"1_SECOND"`: Every second
- `"5_SECOND"`: Every 5 seconds
- `"1_MINUTE"`: At minute end
- `"5_MINUTE"`: At start (for 1-minute simulations)
- `"1_HOUR"`: At start (for 1-minute simulations)

**Example:**

```python
simulator = PriceSimulator()
simulator.log_price("1_SECOND", 154.12)
```

## Configuration Management

### ConfigManager

Manages configuration loading, validation, and environment variable overrides.

 Constructor

```python
ConfigManager(config_file: Optional[str] = None)
```

**Parameters:**

- `config_file` (str): Optional path to configuration file

 Methods

### `get_simulation_config() -> SimulationConfig`

Returns the current simulation configuration.

### `get_security_config() -> SecurityConfig`

Returns the current security configuration.

### `save_config(filename: Optional[str] = None) -> None`

Saves current configuration to file.

### `print_config() -> None`

Prints current configuration to console.

### SimulationConfig

Configuration dataclass for simulation parameters.

**Attributes:**

- `volatility` (float): Price movement randomness (0.0-2.0)
- `duration_seconds` (int): Simulation duration
- `data_file` (str): Market data file path
- `output_file` (str): Results output file
- `log_level` (str): Logging level
- `log_format` (str): Log format string
- `log_date_format` (str): Date format string
- `max_file_size_mb` (int): Maximum file size limit
- `sleep_precision_ms` (float): Timing precision
- `max_price_history` (int): Maximum price records to keep

### SecurityConfig

Configuration dataclass for security settings.

**Attributes:**

- `max_json_depth` (int): Maximum JSON nesting depth
- `max_json_size_kb` (int): Maximum JSON file size
- `allowed_keys` (set): Allowed JSON keys
- `prevent_path_traversal` (bool): Enable path traversal prevention
- `sanitize_filenames` (bool): Enable filename sanitization
- `redact_sensitive_data` (bool): Enable sensitive data redaction

## Environment Variables

The simulator supports configuration via environment variables:

- `FAKE_TRADING_VOLATILITY`: Set volatility (float)
- `FAKE_TRADING_DURATION`: Set simulation duration (int)
- `FAKE_TRADING_DATA_FILE`: Set data file path (str)
- `FAKE_TRADING_OUTPUT_FILE`: Set output file path (str)
- `FAKE_TRADING_LOG_LEVEL`: Set logging level (str)

**Example:**

```bash
export FAKE_TRADING_VOLATILITY=0.3
export FAKE_TRADING_DURATION=120
python faketrading.py
```

## Error Handling

### Common Exceptions

#### `FileNotFoundError`

Raised when market data file is not found.

**Handling:**

```python
try:
    simulator = PriceSimulator(data_file="missing.json")
    market_data = simulator.load_market_data()
except FileNotFoundError as e:
    print(f"Data file not found: {e}")
```

#### `ValueError`

Raised when data validation fails.

**Common Causes:**

- Malformed JSON
- Missing required keys
- Invalid price constraints
- Invalid configuration values

**Handling:**

```python
try:
    simulator = PriceSimulator()
    market_data = simulator.load_market_data()
except ValueError as e:
    print(f"Validation error: {e}")
```

#### `KeyboardInterrupt`

Raised when simulation is interrupted by user.

**Handling:**

```python
try:
    simulator = PriceSimulator()
    results = simulator.run_simulation()
except KeyboardInterrupt:
    print("Simulation interrupted by user")
```

## Security Considerations

### Input Validation

All external inputs are validated:

- JSON structure and data types
- File paths and names
- Configuration values
- Market data constraints

### Path Traversal Prevention

File paths are sanitized to prevent directory traversal attacks:

```python
# SECURITY: Sanitize filename
safe_filename = Path(filename).name  # Removes path components
```

### Allow-List Validation

Critical inputs use allow-list validation:

```python
# SECURITY: Allow-list for interval types
allowed_intervals = {"1_SECOND", "5_SECOND", "1_MINUTE", "5_MINUTE", "1_HOUR"}
if interval not in allowed_intervals:
    raise ValueError(f"Invalid interval: {interval}")
```

## Performance Considerations

### Memory Usage

- Price history is limited to prevent memory leaks
- Large files are rejected to prevent DoS attacks
- Temporary objects are cleaned up automatically

### Timing Precision

- Uses `time.sleep()` for precise timing control
- Compensates for processing overhead
- Maintains consistent 1-second intervals

### Scalability

- Single-threaded design for simplicity
- No external dependencies for reliability
- Minimal resource requirements

## Testing

### Unit Tests

Comprehensive test suite covers:

- Input validation
- Price generation algorithms
- Security measures
- Error handling
- Configuration management

### Running Tests

```bash
# Run all tests
python test_faketrading.py

# With coverage
python -m pytest test_faketrading.py --cov=faketrading --cov-report=html
```

### Test Categories

- **Validation Tests**: Market data and configuration validation
- **Security Tests**: Input sanitization and path traversal prevention
- **Algorithm Tests**: Price generation and convergence
- **Integration Tests**: End-to-end simulation execution

## Best Practices

### Configuration

1. Use environment variables for deployment-specific settings
2. Validate configuration on startup
3. Provide sensible defaults
4. Document all configuration options

 Error Handling

1. Catch specific exceptions, not generic ones
2. Provide meaningful error messages
3. Log errors with appropriate detail
4. Gracefully handle interruptions

### Security

1. Validate all external inputs
2. Use allow-list validation for critical inputs
3. Sanitize file paths and names
4. Implement bounds checking

### Performance

1. Use efficient data structures
2. Limit memory usage
3. Implement proper cleanup
4. Monitor resource consumption

## Examples

### Basic Usage

```python
from faketrading import PriceSimulator

# Create simulator
simulator = PriceSimulator(volatility=0.5)

# Run simulation
results = simulator.run_simulation()

# Export results
simulator.export_results("results.json")
```

### Custom Configuration

```python
from faketrading import PriceSimulator
from config import get_config

# Get configuration
config = get_config()
sim_config = config.get_simulation_config()

# Create simulator with custom settings
simulator = PriceSimulator(
    volatility=sim_config.volatility,
    data_file=sim_config.data_file
)

# Run simulation
results = simulator.run_simulation()
```

 Error Handling

```python
from faketrading import PriceSimulator

try:
    simulator = PriceSimulator()
    results = simulator.run_simulation()
    simulator.export_results("results.json")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except ValueError as e:
    print(f"Validation error: {e}")
except KeyboardInterrupt:
    print("Simulation interrupted")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

*This API documentation is part of the Fake Trading Price Simulator project.*
