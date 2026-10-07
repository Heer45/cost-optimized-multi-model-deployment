import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')  # type: ignore[union-attr]

from cost_simulator import CostSimulator

def main():
    print("=== COST SIMULATION TEST ===\n")
    
    # Initialize our dynamic simulator (Loads directly from Phase 3A measured JSON footprint)
    # Does not change, touch, or retrain any scikit-learn models.
    simulator = CostSimulator()
    profile = simulator.get_cost_profile()
    
    for model_name, data in profile.items():
        print(f"{model_name}")
        print(f"Latency: {data['latency_ms']:.4f} ms")
        print(f"Ratio: {data['latency_ratio']:.4f}")
        print(f"Simulated Cost: ₹{data['simulated_cost']:.4f}\n")
        
    print("=== COST COMPARISON ===\n")
    
    selected = "Model A"
    alternative_b = "Model B"
    alternative_c = "Model C"
    
    costs = simulator.compare_request_costs()
    
    print(f"Selected Model: {selected}")
    for model_name, cost in costs.items():
        print(f"{model_name} Cost: ₹{cost:.4f}")
        
    print()
    
    # Showcase dynamic mathematical savings vs the alternative routed models
    savings_vs_b = simulator.calculate_savings(selected, alternative_b)
    print(f"Potential Savings vs {alternative_b}: ₹{savings_vs_b['savings']:.4f} ({savings_vs_b['savings_percentage']:.2f}%)")
    
    savings_vs_c = simulator.calculate_savings(selected, alternative_c)
    print(f"Potential Savings vs {alternative_c}: ₹{savings_vs_c['savings']:.4f} ({savings_vs_c['savings_percentage']:.2f}%)")

if __name__ == "__main__":
    main()