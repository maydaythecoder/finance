#!/usr/bin/env python3
"""
Fake Trading Price Simulator

Simulates realistic price movement within a defined range, converging precisely
on a known closing price after 60 seconds with controllable volatility.

SECURITY: Input validation prevents malformed JSON exploitation
SAFETY: Price bounds enforcement prevents unrealistic market conditions
"""

import json
import time
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import sys

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class PriceSimulator:
    """
    Simulates price movements with convergence to target close price.
    
    SECURITY: Validates all inputs to prevent injection attacks
    SAFETY: Enforces price bounds and validates JSON structure
    """
    
    def __init__(self, volatility: float = 0.5, data_file: str = "data.json"):
        self.volatility = volatility
        self.data_file = data_file
        self.price_log: List[Dict[str, Any]] = []
        self.current_price: float = 0.0
        self.market_data: Dict[str, float] = {}
        
    def load_market_data(self) -> Dict[str, float]:
        """
        Load and validate market data from JSON file.
        
        SECURITY: Validates JSON structure to prevent malformed data exploitation
        SAFETY: Ensures high >= low constraint for realistic market conditions
        """
        try:
            data_path = Path(self.data_file)
            if not data_path.exists():
                raise FileNotFoundError(f"Market data file not found: {self.data_file}")
                
            with open(data_path, 'r') as f:
                data = json.load(f)
                
            # SECURITY: Validate required keys to prevent KeyError exploitation
            required_keys = {"open", "high", "low", "close"}
            if not required_keys.issubset(data.keys()):
                missing = required_keys - data.keys()
                raise ValueError(f"Missing required keys in JSON: {missing}")
                
            # SAFETY: Validate numeric types and logical constraints
            for key in required_keys:
                if not isinstance(data[key], (int, float)):
                    raise ValueError(f"Value for '{key}' must be numeric, got {type(data[key])}")
                    
            if data["high"] < data["low"]:
                raise ValueError(f"High price ({data['high']}) cannot be less than low price ({data['low']})")
                
            # Additional market realism checks
            if data["open"] < data["low"] or data["open"] > data["high"]:
                raise ValueError(f"Open price ({data['open']}) must be within low-high range")
                
            if data["close"] < data["low"] or data["close"] > data["high"]:
                raise ValueError(f"Close price ({data['close']}) must be within low-high range")
                
            logger.info(f"Loaded market data: Open=${data['open']:.2f}, High=${data['high']:.2f}, Low=${data['low']:.2f}, Close=${data['close']:.2f}")
            return data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {self.data_file}: {e}")
        except Exception as e:
            logger.error(f"Failed to load market data: {e}")
            raise
            
    def generate_price(self, second: int, total_seconds: int = 60) -> float:
        """
        Generate next price using controlled random walk with convergence bias.
        
        SAFETY: Implements convergence algorithm to ensure target close price
        Algorithm uses weighted bias toward target with decreasing randomness over time
        """
        # Calculate convergence weight (increases over time to ensure target hit)
        convergence_weight = min(0.9, second / total_seconds)
        
        # Calculate target bias - stronger as we approach end
        target_bias = (self.market_data["close"] - self.current_price) * convergence_weight
        
        # Generate random component with volatility scaling
        # SAFETY: Use normal distribution to prevent extreme outliers
        random_component = random.gauss(0, self.volatility) * (1 - convergence_weight)
        
        # Calculate proposed new price
        price_change = target_bias + random_component
        new_price = self.current_price + price_change
        
        # SAFETY: Enforce market bounds to prevent unrealistic prices
        new_price = max(self.market_data["low"], min(self.market_data["high"], new_price))
        
        return new_price
        
    def log_price(self, interval: str, price: float, timestamp: datetime = None) -> None:
        """
        Log price data with structured format.
        
        SECURITY: Sanitizes interval string to prevent log injection
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        # SECURITY: Sanitize interval string (allow-list approach)
        allowed_intervals = {"1_SECOND", "5_SECOND", "1_MINUTE", "5_MINUTE", "1_HOUR"}
        if interval not in allowed_intervals:
            logger.warning(f"Invalid interval type: {interval}")
            return
            
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "interval": interval,
            "price": round(price, 2)
        }
        
        self.price_log.append(log_entry)
        
        # Format output for console
        formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{formatted_time}] [{interval}] Price: ${price:.2f}")
        
    def should_log_interval(self, second: int, interval_type: str) -> bool:
        """
        Determine if current second should trigger interval logging.
        
        SAFETY: Prevents division by zero and handles edge cases
        """
        if interval_type == "1_SECOND":
            return True
        elif interval_type == "5_SECOND":
            return second % 5 == 0
        elif interval_type == "1_MINUTE":
            return second == 59  # Log at end of minute
        elif interval_type == "5_MINUTE":
            return second == 0   # Only at start for 1-minute simulation
        elif interval_type == "1_HOUR":
            return second == 0   # Only at start for 1-minute simulation
        return False
        
    def run_simulation(self) -> List[Dict[str, Any]]:
        """
        Execute 60-second price simulation with multi-interval logging.
        
        SAFETY: Implements precise timing control and guaranteed convergence
        """
        try:
            # Load and validate market data
            self.market_data = self.load_market_data()
            self.current_price = self.market_data["open"]
            
            logger.info(f"Starting simulation with volatility={self.volatility}")
            start_time = time.time()
            simulation_start = datetime.now()
            
            # Log initial price at multiple intervals
            if self.should_log_interval(0, "1_SECOND"):
                self.log_price("1_SECOND", self.current_price, simulation_start)
            if self.should_log_interval(0, "5_SECOND"):
                self.log_price("5_SECOND", self.current_price, simulation_start)
            if self.should_log_interval(0, "5_MINUTE"):
                self.log_price("5_MINUTE", self.current_price, simulation_start)
            if self.should_log_interval(0, "1_HOUR"):
                self.log_price("1_HOUR", self.current_price, simulation_start)
                
            # Main simulation loop (59 iterations for seconds 1-59)
            for second in range(1, 60):
                # Generate new price with convergence bias
                self.current_price = self.generate_price(second)
                
                # Calculate precise timestamp for this second
                current_time = simulation_start.replace(
                    second=(simulation_start.second + second) % 60,
                    minute=simulation_start.minute + (simulation_start.second + second) // 60
                )
                
                # Log at appropriate intervals
                if self.should_log_interval(second, "1_SECOND"):
                    self.log_price("1_SECOND", self.current_price, current_time)
                if self.should_log_interval(second, "5_SECOND"):
                    self.log_price("5_SECOND", self.current_price, current_time)
                if self.should_log_interval(second, "1_MINUTE"):
                    self.log_price("1_MINUTE", self.current_price, current_time)
                    
                # SAFETY: Precise timing control to maintain 1-second intervals
                elapsed = time.time() - start_time
                target_elapsed = second
                if elapsed < target_elapsed:
                    time.sleep(target_elapsed - elapsed)
                    
            # SAFETY: Force exact convergence to target close price
            self.current_price = self.market_data["close"]
            final_time = simulation_start.replace(
                second=(simulation_start.second + 60) % 60,
                minute=simulation_start.minute + (simulation_start.second + 60) // 60
            )
            self.log_price("1_MINUTE", self.current_price, final_time)
            
            logger.info(f"Simulation complete. Final price set to target close: ${self.current_price:.2f}")
            return self.price_log
            
        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            raise
            
    def export_results(self, filename: str = "simulation_results.json") -> None:
        """
        Export simulation results to JSON file.
        
        SECURITY: Validates filename to prevent path traversal attacks
        """
        try:
            # SECURITY: Sanitize filename (allow-list approach)
            safe_filename = Path(filename).name  # Removes any path components
            if not safe_filename.endswith('.json'):
                safe_filename += '.json'
                
            output_data = {
                "simulation_metadata": {
                    "volatility": self.volatility,
                    "data_file": self.data_file,
                    "market_data": self.market_data,
                    "total_records": len(self.price_log)
                },
                "price_data": self.price_log
            }
            
            with open(safe_filename, 'w') as f:
                json.dump(output_data, f, indent=2)
                
            logger.info(f"Results exported to {safe_filename}")
            
        except Exception as e:
            logger.error(f"Failed to export results: {e}")
            raise

def main():
    """
    Main entry point for the price simulation.
    
    SAFETY: Implements error handling and graceful shutdown
    """
    try:
        # Configuration
        volatility = 0.5  # Configurable volatility parameter
        data_file = "data.json"
        
        # Create and run simulator
        simulator = PriceSimulator(volatility=volatility, data_file=data_file)
        results = simulator.run_simulation()
        
        # Export results
        simulator.export_results("simulation_results.json")
        
        # Summary statistics
        print(f"\nSimulation Summary:")
        print(f"Total price updates: {len(results)}")
        print(f"Volatility setting: {volatility}")
        print(f"Target achieved: ${simulator.current_price:.2f}")
        
    except KeyboardInterrupt:
        logger.info("Simulation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
