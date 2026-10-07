import numpy as np
from sklearn.datasets import load_breast_cancer
from model_manager import ModelManager
from router import SmartRouter

# Class names for the Breast Cancer dataset: index 0 = Malignant, 1 = Benign
TARGET_NAMES: list[str] = ["Malignant", "Benign"]

def main():
    # 1. Initialize our decoupled components
    manager = ModelManager()
    manager.load_models()
    
    router = SmartRouter()
    
    # 2. Get real sample data from the exact Breast Cancer dataset.
    # return_X_y=True returns plain ndarrays, avoiding Bunch attribute ambiguity.
    X, y = load_breast_cancer(return_X_y=True)
    # Scikit-learn expects 2D arrays for predictions: X[0:1] natively handles this
    sample_input_1 = X[0:1] # Taking the 1st row
    sample_input_2 = X[1:2] # Taking the 2nd row
    
    print("\n--- Starting Routing & Prediction Tests ---\n")
    
    def process_request(complexity, input_data, request_id):
        print(f"--- Request {request_id} ---")
        
        # 1. Ask router for independent decision
        route_info = router.route(input_data)
        model_name = route_info['selected_model']
        
        print(f"Input Complexity: {route_info['complexity']}")
        print(f"Selected Model:   {route_info['selected_model']}")
        print(f"Reason:           {route_info['reason']}")
        
        # 2. Feed decision to Model Manager to get actual scikit-learn prediction
        prediction = manager.predict(model_name, input_data)
        
        # Convert numeric target (0 or 1) to actual class names for better reading
        # Based on sklearn dataset targets: 0 = Malignant, 1 = Benign
        class_name = TARGET_NAMES[prediction[0]]
        print(f"Prediction:       {prediction[0]} ({class_name.capitalize()})\n")
        return model_name
        
    # Sequence testing
    # Simple -> Model A
    process_request("Simple", sample_input_1, 1)
    
    # Medium -> Model B
    process_request("Medium", sample_input_1, 2)
    
    # Complex -> Model C
    process_request("Complex", sample_input_1, 3)

    # Dynamic Switching Demo explicitly proving the statless per-request setup
    print("=== DYNAMIC PER-REQUEST SWITCHING TEST ===\n")
    
    # First ask for a complex model route
    m1 = process_request("Complex", sample_input_2, 4)
    
    # Immediately ask for a simple model route
    m2 = process_request("Simple", sample_input_2, 5)
    
    if m1 == "Model C" and m2 == "Model A":
        print("SUCCESS! The system successfully and independently switched from Model C directly back to Model A on a per-request basis.")
        
if __name__ == "__main__":
    main()
