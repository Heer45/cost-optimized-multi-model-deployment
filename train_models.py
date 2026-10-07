import os
import joblib
import pandas as pd
from typing import cast
from sklearn.datasets import load_breast_cancer
from sklearn.utils import Bunch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def evaluate_and_print(model_name, y_true, y_pred):
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    
    print(f"{model_name}:")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1:        {f1:.4f}")
    print("-" * 30)

def main():
    print("Loading Breast Cancer Wisconsin dataset...")
    data = cast(Bunch, load_breast_cancer(return_X_y=False))
    X = data.data
    y = data.target

    # Split dataset - Using stratify to maintain class distribution, avoiding data leakage
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print(f"Train set size: {X_train.shape[0]}")
    print(f"Test set size: {X_test.shape[0]}")
    print("-" * 30)

    # Define models
    # We use Pipeline to ensure that preprocessing (like StandardScaler for LogisticRegression) 
    # is bundled with the model. This prevents data leakage during scaling and simplifies inference later.
    models = {
        "Model A (Logistic Regression)": Pipeline([
            ('scaler', StandardScaler()),
            ('clf', LogisticRegression(random_state=42))
        ]),
        "Model B (Random Forest)": Pipeline([
            ('clf', RandomForestClassifier(random_state=42))
        ]),
        "Model C (Gradient Boosting)": Pipeline([
            ('clf', GradientBoostingClassifier(random_state=42))
        ])
    }

    # Ensure models directory exists
    os.makedirs('models', exist_ok=True)
    
    file_names = {
        "Model A (Logistic Regression)": "model_a.pkl",
        "Model B (Random Forest)": "model_b.pkl",
        "Model C (Gradient Boosting)": "model_c.pkl"
    }

    # Train, evaluate, and save
    for name, pipeline in models.items():
        # Train
        pipeline.fit(X_train, y_train)
        
        # Evaluate
        y_pred = pipeline.predict(X_test)
        evaluate_and_print(name, y_test, y_pred)
        
        # Save
        model_path = os.path.join('models', file_names[name])
        joblib.dump(pipeline, model_path)
        print(f"Saved {name} to {model_path}\n")

if __name__ == "__main__":
    main()
