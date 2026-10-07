"""
This is a simulated educational cost metric derived from measured local inference latency.
It is NOT an actual cloud billing rate. It translates our collected performance profiling latency 
into a normalized theoretical currency format to visualize comparative computational expense.
"""

import json
import os

class CostSimulator:
    def __init__(self, baseline_cost=0.01, profile_path='latency_profile.json'):
        self.baseline_cost = baseline_cost
        self.profile_path = profile_path
        self.latencies = {}
        self.baseline_latency = None
        self.load_latencies()

    def load_latencies(self):
        """Loads latency values measured dynamically during Phase 3A."""
        if not os.path.exists(self.profile_path):
            raise FileNotFoundError(f"Latency profile {self.profile_path} missing. Please run profile_models.py first.")
            
        with open(self.profile_path, 'r') as f:
            self.latencies = json.load(f)
            
        if "Model A" not in self.latencies:
            raise KeyError("Model A latency data missing. Cannot establish baseline.")
            
        self.baseline_latency = self.latencies["Model A"]

    def calculate_model_cost(self, model_name):
        """
        Calculates normalized simulated metric dynamically using Model A as a ~1.0 baseline.
        This approach cleanly decouples resource costs from pure arbitrary ML accuracy.
        """
        if model_name not in self.latencies:
            raise ValueError(f"Unknown model Name: {model_name}")
            
        model_latency = self.latencies[model_name]
        
        # Calculate ratio: e.g. Model B latency (30ms) / Model A latency (1ms) = ~30.0
        latency_ratio = model_latency / self.baseline_latency
        
        # Calculate fictional educational price: Base(₹0.01) * Ratio (~30.0) = ₹0.30
        simulated_cost = self.baseline_cost * latency_ratio
        
        return {
            "latency_ms": model_latency,
            "latency_ratio": latency_ratio,
            "simulated_cost": simulated_cost
        }

    def get_cost_profile(self):
        """Generates a complete dictionary of all calculated cost data."""
        return {model: self.calculate_model_cost(model) for model in self.latencies.keys()}

    def compare_request_costs(self):
        """Returns a clean snapshot of purely monetary comparisons (used later by UI)."""
        return {model: self.calculate_model_cost(model)["simulated_cost"] for model in self.latencies.keys()}
        
    def calculate_savings(self, selected_model, alternative_model):
        """
        Calculates the theoretical savings metric if selected_model was routed 
        instead of the heavier alternative_model. Handles negatives/zeros safely.
        """
        sel_cost = self.calculate_model_cost(selected_model)["simulated_cost"]
        alt_cost = self.calculate_model_cost(alternative_model)["simulated_cost"]
        
        savings = alt_cost - sel_cost
        
        if alt_cost > 0:
            savings_pct = (savings / alt_cost) * 100
        else:
            savings_pct = 0
            
        return {
            "savings": savings,
            "savings_percentage": savings_pct
        }