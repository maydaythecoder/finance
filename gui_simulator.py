#!/usr/bin/env python3
"""
GUI for Fake Trading Price Simulator

SECURITY: GUI input validation and sanitization
SAFETY: Real-time simulation control with bounds checking
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import queue

# Try to import matplotlib for candlestick charts
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    from matplotlib.patches import Rectangle
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Matplotlib not available. Install it to enable candlestick charts.")

# Import our simulator
from faketrading import PriceSimulator


class TradingSimulatorGUI:
    """GUI application for the Fake Trading Price Simulator."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Fake Trading Price Simulator")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Simulation state
        self.simulator: Optional[PriceSimulator] = None
        self.simulation_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.pause_simulation = False
        
        # Data queue for thread communication
        self.data_queue = queue.Queue()
        
        # GUI variables
        self.volatility_var = tk.DoubleVar(value=0.5)
        self.duration_var = tk.IntVar(value=60)
        # Candle interval selector (default 1 second)
        self.candle_interval_var = tk.StringVar(value="1 sec")
        self.data_file_var = tk.StringVar(value="data.json")
        self.output_file_var = tk.StringVar(value="simulation_results.json")
        self.log_level_var = tk.StringVar(value="INFO")
        
        # Price history for plotting
        self.price_history = []
        self.time_history = []
        
        # Candlestick aggregation and chart objects
        self.candlestick_data = []  # List[Dict[str, float]]
        self.current_candle = None
        self.figure = None
        self.canvas = None
        self.ax = None
        
        self.setup_gui()
        self.setup_bindings()
        
    def setup_gui(self):
        """Setup the GUI layout."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Control Panel (Left)
        self.setup_control_panel(main_frame)
        
        # Display Panel (Right)
        self.setup_display_panel(main_frame)
        
        # Status Bar
        self.setup_status_bar(main_frame)
        
        # Load market data after GUI is setup
        self.load_market_data()
        
    def setup_control_panel(self, parent):
        """Setup the control panel with configuration options."""
        control_frame = ttk.LabelFrame(parent, text="Control Panel", padding="10")
        control_frame.grid(row=0, column=0, rowspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Simulation Parameters
        params_frame = ttk.LabelFrame(control_frame, text="Simulation Parameters", padding="5")
        params_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Volatility
        ttk.Label(params_frame, text="Volatility:").grid(row=0, column=0, sticky=tk.W, pady=2)
        volatility_scale = ttk.Scale(params_frame, from_=0.0, to=2.0, 
                                   variable=self.volatility_var, orient=tk.HORIZONTAL)
        volatility_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        ttk.Label(params_frame, textvariable=tk.StringVar(value="0.5")).grid(row=0, column=2, padx=(5, 0))
        
        # Candle Interval Selector
        ttk.Label(params_frame, text="Candle Interval:").grid(row=1, column=0, sticky=tk.W, pady=2)
        interval_combo = ttk.Combobox(params_frame, textvariable=self.candle_interval_var,
                                      values=["1 sec", "5 sec", "1 min", "5 min"],
                                      state="readonly", width=10)
        interval_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        # Log Level
        ttk.Label(params_frame, text="Log Level:").grid(row=2, column=0, sticky=tk.W, pady=2)
        log_combo = ttk.Combobox(params_frame, textvariable=self.log_level_var, 
                               values=["DEBUG", "INFO", "WARNING", "ERROR"], 
                               state="readonly", width=10)
        log_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        # File Configuration
        file_frame = ttk.LabelFrame(control_frame, text="File Configuration", padding="5")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Data File
        ttk.Label(file_frame, text="Data File:").grid(row=0, column=0, sticky=tk.W, pady=2)
        data_entry = ttk.Entry(file_frame, textvariable=self.data_file_var, width=20)
        data_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(file_frame, text="Browse", command=self.browse_data_file).grid(row=0, column=2, pady=2)
        
        # Output File
        ttk.Label(file_frame, text="Output File:").grid(row=1, column=0, sticky=tk.W, pady=2)
        output_entry = ttk.Entry(file_frame, textvariable=self.output_file_var, width=20)
        output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(file_frame, text="Browse", command=self.browse_output_file).grid(row=1, column=2, pady=2)
        
        # Market Data Display
        market_frame = ttk.LabelFrame(control_frame, text="Market Data", padding="5")
        market_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.market_data_text = tk.Text(market_frame, height=6, width=30)
        self.market_data_text.pack(fill=tk.BOTH, expand=True)
        
        # Control Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="Start Simulation", 
                                     command=self.start_simulation)
        self.start_button.pack(fill=tk.X, pady=2)
        
        self.pause_button = ttk.Button(button_frame, text="Pause", 
                                     command=self.pause_simulation_toggle, state=tk.DISABLED)
        self.pause_button.pack(fill=tk.X, pady=2)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                    command=self.stop_simulation, state=tk.DISABLED)
        self.stop_button.pack(fill=tk.X, pady=2)
        
        self.reset_button = ttk.Button(button_frame, text="Reset", 
                                     command=self.reset_simulation)
        self.reset_button.pack(fill=tk.X, pady=2)
        
    def setup_display_panel(self, parent):
        """Setup the display panel with real-time data."""
        display_frame = ttk.LabelFrame(parent, text="Simulation Display", padding="10")
        display_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Current Price Display
        price_frame = ttk.Frame(display_frame)
        price_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(price_frame, text="Current Price:", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        self.current_price_label = ttk.Label(price_frame, text="$0.00", 
                                           font=("Arial", 16, "bold"), foreground="green")
        self.current_price_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Progress Bar
        progress_frame = ttk.Frame(display_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(progress_frame, text="Progress:").pack(side=tk.LEFT)
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=300)
        self.progress_bar.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        self.progress_label = ttk.Label(progress_frame, text="0/60 seconds")
        self.progress_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Candlestick Chart
        chart_frame = ttk.LabelFrame(display_frame, text="Price Chart (Candlesticks)", padding="5")
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        if MATPLOTLIB_AVAILABLE:
            self.figure = Figure(figsize=(8, 4), dpi=100)
            self.ax = self.figure.add_subplot(111)
            self.ax.set_title("Real-time Candlestick Chart")
            self.ax.set_xlabel("Time (seconds)")
            self.ax.set_ylabel("Price ($)")
            self.ax.grid(True, alpha=0.3)
            
            self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            ttk.Label(chart_frame, text="Matplotlib is required for candlestick charts.\nInstall with: pip install matplotlib").pack(fill=tk.BOTH, expand=True)
        
        # Log Display
        log_frame = ttk.LabelFrame(display_frame, text="Simulation Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.log_text = tk.Text(log_frame, height=8, width=50)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_status_bar(self, parent):
        """Setup the status bar."""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=1, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        self.simulation_time_label = ttk.Label(status_frame, text="")
        self.simulation_time_label.pack(side=tk.RIGHT)
        
    def setup_bindings(self):
        """Setup event bindings."""
        # Update progress when volatility changes
        self.volatility_var.trace_add('write', self.on_volatility_change)
        
        # Update display periodically
        self.root.after(100, self.update_display)
        
    def browse_data_file(self):
        """Browse for data file."""
        filename = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.data_file_var.set(filename)
            self.load_market_data()
            
    def browse_output_file(self):
        """Browse for output file."""
        filename = filedialog.asksaveasfilename(
            title="Save Output File",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.output_file_var.set(filename)
            
    def load_market_data(self):
        """Load and display market data."""
        try:
            data_file = self.data_file_var.get()
            if Path(data_file).exists():
                with open(data_file, 'r') as f:
                    data = json.load(f)
                
                # Display market data
                market_info = f"""Open: ${data['open']:.2f}
High: ${data['high']:.2f}
Low: ${data['low']:.2f}
Close: ${data['close']:.2f}
Range: ${data['high'] - data['low']:.2f}"""
                
                self.market_data_text.delete(1.0, tk.END)
                self.market_data_text.insert(1.0, market_info)
                
                # Update current price
                self.current_price_label.config(text=f"${data['open']:.2f}")
                
                self.log_message("Market data loaded successfully")
            else:
                self.log_message(f"Data file not found: {data_file}", "ERROR")
        except Exception as e:
            self.log_message(f"Error loading market data: {e}", "ERROR")
            
    def on_volatility_change(self, *args):
        """Handle volatility change."""
        volatility = self.volatility_var.get()
        self.log_message(f"Volatility changed to: {volatility:.2f}")
        
    def start_simulation(self):
        """Start the simulation in a separate thread."""
        if self.is_running:
            return
            
        try:
            # Create simulator with current settings
            self.simulator = PriceSimulator(
                volatility=self.volatility_var.get(),
                data_file=self.data_file_var.get()
            )
            
            # Clear previous data
            self.price_history = []
            self.time_history = []
            if MATPLOTLIB_AVAILABLE and self.ax is not None:
                self.ax.clear()
                self.ax.set_title("Real-time Candlestick Chart")
                self.ax.set_xlabel("Time (seconds)")
                self.ax.set_ylabel("Price ($)")
                self.ax.grid(True, alpha=0.3)
                self.candlestick_data = []
                self.current_candle = None
                self.canvas.draw()
            self.log_text.delete(1.0, tk.END)
            
            # Start simulation thread
            self.is_running = True
            self.pause_simulation = False
            self.simulation_thread = threading.Thread(target=self.run_simulation_thread)
            self.simulation_thread.daemon = True
            self.simulation_thread.start()
            
            # Update UI
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text="Simulation Running")
            
            self.log_message("Simulation started")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start simulation: {e}")
            self.log_message(f"Error starting simulation: {e}", "ERROR")
            
    def run_simulation_thread(self):
        """Run simulation in separate thread."""
        try:
            # Load market data
            market_data = self.simulator.load_market_data()
            self.simulator.current_price = market_data["open"]
            
            # Send initial data
            self.data_queue.put({
                'type': 'price_update',
                'price': self.simulator.current_price,
                'second': 0,
                'interval': '1_SECOND'
            })
            
            # Run simulation
            duration = self.duration_var.get()
            start_time = time.time()
            
            for second in range(1, duration + 1):
                if not self.is_running:
                    break
                    
                # Wait for pause to be released
                while self.pause_simulation and self.is_running:
                    time.sleep(0.1)
                    
                if not self.is_running:
                    break
                    
                # Generate next price
                self.simulator.current_price = self.simulator.generate_price(second, duration)
                
                # Send data to GUI
                self.data_queue.put({
                    'type': 'price_update',
                    'price': self.simulator.current_price,
                    'second': second,
                    'interval': '1_SECOND'
                })
                
                # Log at intervals
                if second % 5 == 0:
                    self.data_queue.put({
                        'type': 'price_update',
                        'price': self.simulator.current_price,
                        'second': second,
                        'interval': '5_SECOND'
                    })
                
                # Sleep for 1 second
                elapsed = time.time() - start_time
                target_elapsed = second
                if elapsed < target_elapsed:
                    time.sleep(target_elapsed - elapsed)
                    
            # Final price (convergence)
            self.simulator.current_price = market_data["close"]
            self.data_queue.put({
                'type': 'price_update',
                'price': self.simulator.current_price,
                'second': duration,
                'interval': '1_MINUTE'
            })
            
            # Export results
            self.simulator.export_results(self.output_file_var.get())
            
            # Send completion signal
            self.data_queue.put({'type': 'simulation_complete'})
            
        except Exception as e:
            self.data_queue.put({
                'type': 'error',
                'message': str(e)
            })
            
    def pause_simulation_toggle(self):
        """Toggle simulation pause."""
        self.pause_simulation = not self.pause_simulation
        if self.pause_simulation:
            self.pause_button.config(text="Resume")
            self.status_label.config(text="Simulation Paused")
            self.log_message("Simulation paused")
        else:
            self.pause_button.config(text="Pause")
            self.status_label.config(text="Simulation Running")
            self.log_message("Simulation resumed")
            
    def stop_simulation(self):
        """Stop the simulation."""
        self.is_running = False
        self.pause_simulation = False
        
        # Update UI
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Simulation Stopped")
        
        self.log_message("Simulation stopped")
        
    def reset_simulation(self):
        """Reset the simulation display."""
        self.price_history = []
        self.time_history = []
        if MATPLOTLIB_AVAILABLE and self.ax is not None:
            self.ax.clear()
            self.ax.set_title("Real-time Candlestick Chart")
            self.ax.set_xlabel("Time (seconds)")
            self.ax.set_ylabel("Price ($)")
            self.ax.grid(True, alpha=0.3)
            self.candlestick_data = []
            self.current_candle = None
            self.canvas.draw()
        self.log_text.delete(1.0, tk.END)
        self.current_price_label.config(text="$0.00")
        self.progress_bar['value'] = 0
        self.progress_label.config(text=f"0/{self.duration_var.get()} seconds")
        self.status_label.config(text="Ready")
        self.simulation_time_label.config(text="")
        
        self.log_message("Display reset")

    def update_candlestick_data(self, second, price):
        """Aggregate tick updates into 5-second OHLC candles."""
        candle_interval = self.get_candle_interval_seconds()
        
        if second % candle_interval == 0:
            # Start a new candle at boundaries; store the previous one
            if self.current_candle is not None:
                self.candlestick_data.append(self.current_candle)
            self.current_candle = {
                'time': second,
                'open': price,
                'high': price,
                'low': price,
                'close': price
            }
        else:
            if self.current_candle is not None:
                self.current_candle['high'] = max(self.current_candle['high'], price)
                self.current_candle['low'] = min(self.current_candle['low'], price)
                self.current_candle['close'] = price

    def update_candlestick_chart(self):
        """Render candlesticks on the chart."""
        if not MATPLOTLIB_AVAILABLE or self.ax is None:
            return
        
        self.ax.clear()
        
        # Include the in-progress candle
        if self.current_candle is not None:
            temp_data = self.candlestick_data + [self.current_candle]
        else:
            temp_data = self.candlestick_data
        
        if len(temp_data) > 0:
            times = [c['time'] for c in temp_data]
            opens = [c['open'] for c in temp_data]
            highs = [c['high'] for c in temp_data]
            lows = [c['low'] for c in temp_data]
            closes = [c['close'] for c in temp_data]
            self.plot_candlesticks(times, opens, highs, lows, closes)
        
        self.ax.set_title("Real-time Candlestick Chart")
        self.ax.set_xlabel("Time (seconds)")
        self.ax.set_ylabel("Price ($)")
        self.ax.grid(True, alpha=0.3)
        
        # Y-limits from market data if available
        if self.simulator and self.simulator.market_data:
            low = self.simulator.market_data['low']
            high = self.simulator.market_data['high']
            margin = (high - low) * 0.1
            self.ax.set_ylim(low - margin, high + margin)
        
        if self.canvas is not None:
            self.canvas.draw()

    def plot_candlesticks(self, times, opens, highs, lows, closes):
        """Draw candle wicks and bodies."""
        for i in range(len(times)):
            t = times[i]
            o = opens[i]
            h = highs[i]
            l = lows[i]
            c = closes[i]
            
            is_bullish = c >= o
            color = 'green' if is_bullish else 'red'
            
            # Wick
            self.ax.plot([t, t], [l, h], color='black', linewidth=1)
            
            # Body
            body_height = abs(c - o)
            if body_height > 0:
                rect = Rectangle((t - 0.2, min(o, c)), 0.4, body_height, facecolor=color, edgecolor='black', linewidth=1)
                self.ax.add_patch(rect)
            else:
                # Doji
                self.ax.plot([t - 0.2, t + 0.2], [o, o], color='black', linewidth=2)

    def get_candle_interval_seconds(self) -> int:
        """Map UI selection to seconds."""
        value = (self.candle_interval_var.get() or "1 sec").strip().lower()
        if value.startswith("5 min"):
            return 300
        if value.startswith("1 min"):
            return 60
        if value.startswith("5 sec"):
            return 5
        return 1
        
    def update_display(self):
        """Update the display with data from the simulation thread."""
        try:
            while True:
                data = self.data_queue.get_nowait()
                
                if data['type'] == 'price_update':
                    self.update_price_display(data)
                elif data['type'] == 'simulation_complete':
                    self.on_simulation_complete()
                elif data['type'] == 'error':
                    messagebox.showerror("Simulation Error", data['message'])
                    self.stop_simulation()
                    
        except queue.Empty:
            pass
        
        # Schedule next update
        self.root.after(100, self.update_display)
        
    def update_price_display(self, data):
        """Update price display with new data."""
        price = data['price']
        second = data['second']
        interval = data['interval']
        
        # Update current price
        self.current_price_label.config(text=f"${price:.2f}")
        
        # Update progress (label reflects candle interval selection)
        duration = self.duration_var.get()
        progress = (second / duration) * 100
        self.progress_bar['value'] = progress
        self.progress_label.config(text=f"{second}/{duration} seconds")
        
        # Add to history
        self.price_history.append(price)
        self.time_history.append(second)
        
        # Update candlestick aggregation and redraw
        if MATPLOTLIB_AVAILABLE and self.ax is not None:
            self.update_candlestick_data(second, price)
            self.update_candlestick_chart()
        
        # Log message
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] [{interval}] Price: ${price:.2f}\n"
        self.log_text.insert(tk.END, log_line)
        self.log_text.see(tk.END)
        
        # Update simulation time
        self.simulation_time_label.config(text=f"Last Update: {timestamp}")
        
    def on_simulation_complete(self):
        """Handle simulation completion."""
        self.is_running = False
        
        # Update UI
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Simulation Complete")
        
        # Draw the final candle state
        if MATPLOTLIB_AVAILABLE and self.ax is not None:
            self.update_candlestick_chart()
            self.canvas.draw()
        
        self.log_message("Simulation completed successfully")
        messagebox.showinfo("Simulation Complete", 
                          f"Simulation completed!\nResults saved to: {self.output_file_var.get()}")
        
    def log_message(self, message: str, level: str = "INFO"):
        """Add message to log display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"
        self.log_text.insert(tk.END, log_line)
        self.log_text.see(tk.END)


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    
    # Set application icon and title
    root.title("Fake Trading Price Simulator - GUI")
    
    # Create and run the GUI
    app = TradingSimulatorGUI(root)
    
    # Start the GUI event loop
    root.mainloop()


if __name__ == "__main__":
    main()
