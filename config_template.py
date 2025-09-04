# Fake Trading Price Simulator - Configuration

# This file contains configuration settings for the simulator
# Copy this file to config.py and modify as needed

# Simulation Configuration
SIMULATION_CONFIG = {
    # Default volatility setting (0.1 = low, 1.0 = high)
    "default_volatility": 0.5,
    
    # Simulation duration in seconds
    "simulation_duration": 60,
    
    # Default data file
    "default_data_file": "data.json",
    
    # Output file for results
    "output_file": "simulation_results.json",
    
    # Logging configuration
    "logging_level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "log_format": "%(asctime)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S"
}

# Security Configuration
SECURITY_CONFIG = {
    # Allowed interval types for logging
    "allowed_intervals": [
        "1_SECOND",
        "5_SECOND", 
        "1_MINUTE",
        "5_MINUTE",
        "1_HOUR"
    ],
    
    # Maximum file size for data files (bytes)
    "max_file_size": 1024 * 1024,  # 1MB
    
    # Allowed file extensions
    "allowed_extensions": [".json"],
    
    # Maximum volatility value to prevent extreme price movements
    "max_volatility": 2.0,
    
    # Minimum time between price updates (seconds)
    "min_update_interval": 0.1
}

# Market Data Validation
MARKET_VALIDATION = {
    # Required keys in market data
    "required_keys": ["open", "high", "low", "close"],
    
    # Maximum price value (prevents unrealistic prices)
    "max_price": 1000000.0,
    
    # Minimum price value
    "min_price": 0.01,
    
    # Maximum price range (high - low)
    "max_price_range": 10000.0
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    # Enable/disable timing control
    "enable_timing": True,
    
    # Timing tolerance (seconds)
    "timing_tolerance": 0.1,
    
    # Maximum number of price records to keep in memory
    "max_records": 10000,
    
    # Enable/disable real-time output
    "real_time_output": True
}

# Development Configuration
DEV_CONFIG = {
    # Enable debug mode
    "debug_mode": False,
    
    # Enable verbose logging
    "verbose_logging": False,
    
    # Enable performance profiling
    "profile_performance": False,
    
    # Test mode (faster simulation for testing)
    "test_mode": False
}
