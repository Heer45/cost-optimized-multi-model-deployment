import sys
from cost_simulator import CostSimulator

cost_sim = CostSimulator()
profile = cost_sim.get_cost_profile()
print(profile)
