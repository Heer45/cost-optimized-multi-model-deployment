import joblib
import os

class ModelManager:
    def __init__(self, models_dir='models'):
        self.models_dir = models_dir
        self.models = {}

    def load_models(self):
        """Loads the pre-trained models from the disk."""
        # Using exact file names as saved in Phase 1
        model_paths = {
            "Model A": "model_a.pkl",
            "Model B": "model_b.pkl",
            "Model C": "model_c.pkl"
        }
        
        for name, file_name in model_paths.items():
            path = os.path.join(self.models_dir, file_name)
            if os.path.exists(path):
                self.models[name] = joblib.load(path)
            else:
                raise FileNotFoundError(f"Model file {path} not found. Please ensure Phase 1 was completed.")
                
        print("Model Manager: All models successfully loaded.")
        
    def predict(self, model_name, input_data):
        """
        Predicts using the specified model.
        input_data should be a suitable format compatible with the models training.
        """
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found. Must be one of {list(self.models.keys())}")
            
        model = self.models[model_name]
        
        # Real prediction call natively tied to scikit-learn pipeline
        prediction = model.predict(input_data)
        
        return prediction