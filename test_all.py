import numpy as np 
from model_manager import ModelManager 
mm = ModelManager() 
mm.load_models() 
fake_data = np.zeros((1, 30)) 
print("A:", mm.predict("Model A", fake_data)) 
print("B:", mm.predict("Model B", fake_data)) 
print("C:", mm.predict("Model C", fake_data)) 
