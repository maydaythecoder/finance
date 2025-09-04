#!/usr/bin/env python3
"""
Configuration management for Fake Trading Price Simulator

SECURITY: Centralized configuration with validation
SAFETY: Type-safe configuration with defaults
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class SimulationConfig:
    """Configuration for simulation parameters."""
    
    # Core simulation settings
    volatility: float = 0.5
    duration_seconds: int = 60
    data_file: str = "data.json"
    output_file: str = "simulation_results.json"
    
    # Logging configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(levelname)s - %(message)s"
    log_date_format: str = "%Y-%m-%d %H:%M:%S"
    
    # Security settings
    max_file_size_mb: int = 10
    allowed_file_extensions: set = field(default_factory=lambda: {".json"})
    
    # Performance settings
    sleep_precision_ms: float = 1.0
    max_price_history: int = 1000
    
    def validate(self) -> None:
        """Validate configuration values."""
        if not (0.0 <= self.volatility <= 2.0):
            raise ValueError(f"Volatility must be between 0.0 and 2.0, got {self.volatility}")
        
        if self.duration_seconds <= 0:
            raise ValueError(f"Duration must be positive, got {self.duration_seconds}")
        
        if not self.data_file.endswith('.json'):
            raise ValueError(f"Data file must have .json extension, got {self.data_file}")
        
        if self.max_file_size_mb <= 0:
            raise ValueError(f"Max file size must be positive, got {self.max_file_size_mb}")


@dataclass
class SecurityConfig:
    """Security-related configuration."""
    
    # Input validation
    max_json_depth: int = 10
    max_json_size_kb: int = 100
    allowed_keys: set = field(default_factory=lambda: {"open", "high", "low", "close"})
    
    # File security
    prevent_path_traversal: bool = True
    sanitize_filenames: bool = True
    
    # Logging security
    redact_sensitive_data: bool = True
    log_sanitization_patterns: set = field(default_factory=lambda: {
        r"password.*=.*",
        r"api_key.*=.*",
        r"secret.*=.*"
    })


class ConfigManager:
    """Manages configuration loading and validation."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config.json"
        self.simulation_config = SimulationConfig()
        self.security_config = SecurityConfig()
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file or environment variables."""
        # Load from file if it exists
        if Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                self._apply_config_data(config_data)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        # Override with environment variables
        self._load_from_environment()
        
        # Validate configuration
        self.simulation_config.validate()
    
    def _apply_config_data(self, config_data: Dict[str, Any]) -> None:
        """Apply configuration data to config objects."""
        if "simulation" in config_data:
            sim_data = config_data["simulation"]
            for key, value in sim_data.items():
                if hasattr(self.simulation_config, key):
                    setattr(self.simulation_config, key, value)
        
        if "security" in config_data:
            sec_data = config_data["security"]
            for key, value in sec_data.items():
                if hasattr(self.security_config, key):
                    setattr(self.security_config, key, value)
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            "FAKE_TRADING_VOLATILITY": ("simulation_config", "volatility", float),
            "FAKE_TRADING_DURATION": ("simulation_config", "duration_seconds", int),
            "FAKE_TRADING_DATA_FILE": ("simulation_config", "data_file", str),
            "FAKE_TRADING_OUTPUT_FILE": ("simulation_config", "output_file", str),
            "FAKE_TRADING_LOG_LEVEL": ("simulation_config", "log_level", str),
        }
        
        for env_var, (config_attr, key, type_cast) in env_mappings.items():
            if env_var in os.environ:
                try:
                    value = type_cast(os.environ[env_var])
                    config_obj = getattr(self, config_attr)
                    setattr(config_obj, key, value)
                except (ValueError, TypeError) as e:
                    print(f"Warning: Invalid environment variable {env_var}: {e}")
    
    def save_config(self, filename: Optional[str] = None) -> None:
        """Save current configuration to file."""
        filename = filename or self.config_file
        
        config_data = {
            "simulation": {
                "volatility": self.simulation_config.volatility,
                "duration_seconds": self.simulation_config.duration_seconds,
                "data_file": self.simulation_config.data_file,
                "output_file": self.simulation_config.output_file,
                "log_level": self.simulation_config.log_level,
                "log_format": self.simulation_config.log_format,
                "log_date_format": self.simulation_config.log_date_format,
                "max_file_size_mb": self.simulation_config.max_file_size_mb,
                "sleep_precision_ms": self.simulation_config.sleep_precision_ms,
                "max_price_history": self.simulation_config.max_price_history,
            },
            "security": {
                "max_json_depth": self.security_config.max_json_depth,
                "max_json_size_kb": self.security_config.max_json_size_kb,
                "prevent_path_traversal": self.security_config.prevent_path_traversal,
                "sanitize_filenames": self.security_config.sanitize_filenames,
                "redact_sensitive_data": self.security_config.redact_sensitive_data,
            }
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(config_data, f, indent=2)
            print(f"Configuration saved to {filename}")
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def get_simulation_config(self) -> SimulationConfig:
        """Get simulation configuration."""
        return self.simulation_config
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration."""
        return self.security_config
    
    def print_config(self) -> None:
        """Print current configuration."""
        print("Current Configuration:")
        print("=" * 50)
        
        print("\nSimulation Settings:")
        for key, value in self.simulation_config.__dict__.items():
            print(f"  {key}: {value}")
        
        print("\nSecurity Settings:")
        for key, value in self.security_config.__dict__.items():
            print(f"  {key}: {value}")


# Global configuration instance
config_manager = ConfigManager()


def get_config() -> ConfigManager:
    """Get the global configuration manager."""
    return config_manager


def get_simulation_config() -> SimulationConfig:
    """Get simulation configuration."""
    return config_manager.get_simulation_config()


def get_security_config() -> SecurityConfig:
    """Get security configuration."""
    return config_manager.get_security_config()


if __name__ == "__main__":
    # Test configuration loading
    config = get_config()
    config.print_config()
    
    # Save default configuration
    config.save_config("config_default.json")
