import os
import joblib
import time
import json
from typing import Any, cast
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def format_size(size_in_bytes):
    return f"{size_in_bytes / 1024:.2f} KB"

def main():
    models_dir = 'models'
    model_paths = {
        "Model A": "model_a.pkl",
        "Model B": "model_b.pkl",
        "Model C": "model_c.pkl"
    }

    data = cast(Any, load_breast_cancer())
    X = data.data
    y = data.target

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    sample_input = X_test[0:1]

    profiling_results = {}

    print("-" * 60)
    print("MODEL PROFILING SCRIPT")
    print("-" * 60)

    for name, path in model_paths.items():
        full_path = os.path.join(models_dir, path)
        file_size_bytes = os.path.getsize(full_path)
        file_size_kb = format_size(file_size_bytes)
        model = joblib.load(full_path)

        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        num_runs = 1000
        for _ in range(10): # Warmup
            model.predict(sample_input)

        start_time = time.perf_counter()
        for _ in range(num_runs):
            model.predict(sample_input)
        end_time = time.perf_counter()

        total_time_ms = (end_time - start_time) * 1000
        avg_latency_ms = total_time_ms / num_runs

        clf = model.named_steps['clf']
        complexity_info = ""
        algo = ""

        if name == "Model A":
            algo = "Logistic Regression"
            complexity_info = f"Features/Coefs: {clf.coef_.shape[1]}"
        elif name == "Model B":
            algo = "Random Forest"
            complexity_info = f"Trees: {clf.n_estimators}"
        elif name == "Model C":
            algo = "Gradient Boosting"
            complexity_info = f"Estimators: {clf.n_estimators}, Max Depth: {clf.max_depth}" 

        profiling_results[name] = {
            "algo": algo,
            "size": file_size_kb,
            "latency": avg_latency_ms,
            "acc": acc,
            "prec": prec,
            "rec": rec,
            "f1": f1,
            "complexity": complexity_info
        }

    # Smallest clean mechanism to export dynamic latencies for Phase 3B cost simulation
    latency_export = {name: data["latency"] for name, data in profiling_results.items()}
    with open('latency_profile.json', 'w') as f:
        json.dump(latency_export, f)

    print("\n------------------------------------------------------------")
    print("MODEL PROFILE (INFERENCE LATENCY & SIZE & COMPLEXITY)")
    print("------------------------------------------------------------")
    print(f"{'Model':<10} {'Algorithm':<21} {'File Size':<12} {'Avg Latency (ms)':<18} {'Complexity'}")

    for name, d in profiling_results.items():
        print(f"{name:<10} {d['algo']:<21} {d['size']:<12} {d['latency']:<18.4f} {d['complexity']}")

if __name__ == "__main__":
    main()