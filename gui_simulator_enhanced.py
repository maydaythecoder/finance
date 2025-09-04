#!/usr/bin/env python3
"""
Enhanced GUI for Fake Trading Price Simulator with Real-time Charting

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

# Try to import matplotlib for charting, fallback to text-based if not available
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Matplotlib not available, using text-based chart")

# Import our simulator
from faketrading import PriceSimulator


class TradingSimulatorGUI:
    """Enhanced GUI application for the Fake Trading Price Simulator."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Fake Trading Price Simulator - Enhanced GUI")
        self.root.geometry("1200x800")
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
        self.data_file_var = tk.StringVar(value="data.json")
        self.output_file_var = tk.StringVar(value="simulation_results.json")
        self.log_level_var = tk.StringVar(value="INFO")
        self.chart_type_var = tk.StringVar(value="Line")
        
        # Price history for plotting
        self.price_history = []
        self.time_history = []
        
        # Chart objects
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
        main_frame.rowconfigure(1, weight=1)
        
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
        control_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Simulation Parameters
        params_frame = ttk.LabelFrame(control_frame, text="Simulation Parameters", padding="5")
        params_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Volatility
        ttk.Label(params_frame, text="Volatility:").grid(row=0, column=0, sticky=tk.W, pady=2)
        volatility_scale = ttk.Scale(params_frame, from_=0.0, to=2.0, 
                                   variable=self.volatility_var, orient=tk.HORIZONTAL)
        volatility_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        self.volatility_label = ttk.Label(params_frame, text="0.5")
        self.volatility_label.grid(row=0, column=2, padx=(5, 0))
        
                # Duration
        ttk.Label(params_frame, text="Duration (seconds):").grid(row=1, column=0, sticky=tk.W, pady=2)
        duration_spin = tk.Spinbox(params_frame, from_=10, to=300,
                                 textvariable=self.duration_var, width=10)
        duration_spin.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        # Log Level
        ttk.Label(params_frame, text="Log Level:").grid(row=2, column=0, sticky=tk.W, pady=2)
        log_combo = ttk.Combobox(params_frame, textvariable=self.log_level_var, 
                               values=["DEBUG", "INFO", "WARNING", "ERROR"], 
                               state="readonly", width=10)
        log_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        # Chart Type (if matplotlib available)
        if MATPLOTLIB_AVAILABLE:
            ttk.Label(params_frame, text="Chart Type:").grid(row=3, column=0, sticky=tk.W, pady=2)
            chart_combo = ttk.Combobox(params_frame, textvariable=self.chart_type_var, 
                                     values=["Line", "Candlestick", "Area"], 
                                     state="readonly", width=10)
            chart_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
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
        
        # Statistics Display
        stats_frame = ttk.LabelFrame(control_frame, text="Statistics", padding="5")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_text = tk.Text(stats_frame, height=4, width=30)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
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
        
        # Chart Display
        if MATPLOTLIB_AVAILABLE:
            self.setup_matplotlib_chart(display_frame)
        else:
            self.setup_text_chart(display_frame)
        
        # Log Display
        log_frame = ttk.LabelFrame(display_frame, text="Simulation Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.log_text = tk.Text(log_frame, height=6, width=50)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def setup_matplotlib_chart(self, parent):
        """Setup matplotlib chart."""
        chart_frame = ttk.LabelFrame(parent, text="Price Chart", padding="5")
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Real-time Price Movement")
        self.ax.set_xlabel("Time (seconds)")
        self.ax.set_ylabel("Price ($)")
        self.ax.grid(True, alpha=0.3)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def setup_text_chart(self, parent):
        """Setup text-based chart fallback."""
        chart_frame = ttk.LabelFrame(parent, text="Price Chart (Text)", padding="5")
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chart_text = tk.Text(chart_frame, height=15, width=50)
        chart_scrollbar = ttk.Scrollbar(chart_frame, orient=tk.VERTICAL, command=self.chart_text.yview)
        self.chart_text.configure(yscrollcommand=chart_scrollbar.set)
        
        self.chart_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chart_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
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
        self.volatility_label.config(text=f"{volatility:.2f}")
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
            if MATPLOTLIB_AVAILABLE:
                self.ax.clear()
                self.ax.set_title("Real-time Price Movement")
                self.ax.set_xlabel("Time (seconds)")
                self.ax.set_ylabel("Price ($)")
                self.ax.grid(True, alpha=0.3)
                self.canvas.draw()
            else:
                self.chart_text.delete(1.0, tk.END)
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
        
        if MATPLOTLIB_AVAILABLE:
            self.ax.clear()
            self.ax.set_title("Real-time Price Movement")
            self.ax.set_xlabel("Time (seconds)")
            self.ax.set_ylabel("Price ($)")
            self.ax.grid(True, alpha=0.3)
            self.canvas.draw()
        else:
            self.chart_text.delete(1.0, tk.END)
            
        self.log_text.delete(1.0, tk.END)
        self.current_price_label.config(text="$0.00")
        self.progress_bar['value'] = 0
        self.progress_label.config(text="0/60 seconds")
        self.status_label.config(text="Ready")
        self.simulation_time_label.config(text="")
        
        # Clear statistics
        self.stats_text.delete(1.0, tk.END)
        
        self.log_message("Display reset")
        
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
        
        # Update progress
        duration = self.duration_var.get()
        progress = (second / duration) * 100
        self.progress_bar['value'] = progress
        self.progress_label.config(text=f"{second}/{duration} seconds")
        
        # Add to history
        self.price_history.append(price)
        self.time_history.append(second)
        
        # Update chart
        if MATPLOTLIB_AVAILABLE:
            self.update_matplotlib_chart()
        else:
            self.update_text_chart(second, interval, price)
        
        # Log message
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] [{interval}] Price: ${price:.2f}\n"
        self.log_text.insert(tk.END, log_line)
        self.log_text.see(tk.END)
        
        # Update simulation time
        self.simulation_time_label.config(text=f"Last Update: {timestamp}")
        
        # Update statistics
        self.update_statistics()
        
    def update_matplotlib_chart(self):
        """Update matplotlib chart."""
        if len(self.price_history) > 1:
            self.ax.clear()
            self.ax.plot(self.time_history, self.price_history, 'b-', linewidth=2)
            self.ax.set_title("Real-time Price Movement")
            self.ax.set_xlabel("Time (seconds)")
            self.ax.set_ylabel("Price ($)")
            self.ax.grid(True, alpha=0.3)
            
            # Set y-axis limits based on market data
            if hasattr(self, 'simulator') and self.simulator.market_data:
                low = self.simulator.market_data['low']
                high = self.simulator.market_data['high']
                margin = (high - low) * 0.1
                self.ax.set_ylim(low - margin, high + margin)
            
            self.canvas.draw()
            
    def update_text_chart(self, second, interval, price):
        """Update text-based chart."""
        chart_line = f"[{second:3d}s] {interval:10s} ${price:8.2f}"
        self.chart_text.insert(tk.END, chart_line + "\n")
        self.chart_text.see(tk.END)
        
        # Keep only last 50 lines
        lines = self.chart_text.get(1.0, tk.END).split('\n')
        if len(lines) > 50:
            self.chart_text.delete(1.0, tk.END)
            self.chart_text.insert(1.0, '\n'.join(lines[-50:]))
            
    def update_statistics(self):
        """Update statistics display."""
        if len(self.price_history) > 1:
            current_price = self.price_history[-1]
            min_price = min(self.price_history)
            max_price = max(self.price_history)
            avg_price = sum(self.price_history) / len(self.price_history)
            
            # Calculate price change
            if len(self.price_history) > 1:
                price_change = current_price - self.price_history[0]
                price_change_pct = (price_change / self.price_history[0]) * 100
            else:
                price_change = 0
                price_change_pct = 0
            
            stats_info = f"""Current: ${current_price:.2f}
Min: ${min_price:.2f}
Max: ${max_price:.2f}
Avg: ${avg_price:.2f}
Change: ${price_change:+.2f} ({price_change_pct:+.2f}%)"""
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats_info)
            
    def on_simulation_complete(self):
        """Handle simulation completion."""
        self.is_running = False
        
        # Update UI
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Simulation Complete")
        
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
    root.title("Fake Trading Price Simulator - Enhanced GUI")
    
    # Create and run the GUI
    app = TradingSimulatorGUI(root)
    
    # Start the GUI event loop
    root.mainloop()


if __name__ == "__main__":
    main()
