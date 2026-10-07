# Cost-Optimized Multi-Model Deployment System

A Streamlit-based ML dashboard that automatically routes patient diagnostic
requests to the most cost-efficient model based on input complexity.

## Architecture

```
Patient (30 features)
      ↓
  SmartRouter  ← automatic complexity scoring
      ↓
 Simple / Medium / Complex
      ↓
Model A / Model B / Model C
      ↓
  ModelManager → Prediction
      ↓
 CostSimulator → Latency & Cost metrics
      ↓
Streamlit Dashboard
```

| Model   | Algorithm             | Accuracy |
|---------|-----------------------|----------|
| Model A | Logistic Regression   | 0.9825   |
| Model B | Random Forest         | 0.9561   |
| Model C | Gradient Boosting     | 0.9561   |

Dataset: sklearn Breast Cancer Wisconsin (30 numerical features).

Cost is a **simulated educational metric** derived from measured local inference
latency — it is not a real cloud billing rate.

## Quick Start

### Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Run tests

```bash
python test_routing.py
```

### Docker

```bash
docker build -t cost-optimized-ml-app .
docker run -p 8501:8501 cost-optimized-ml-app
```

Then open **http://localhost:8501** in a browser.

## DevOps Pipeline (Jenkins)

The included `Jenkinsfile` defines a four-stage declarative pipeline:

```
GitHub → Jenkins → Checkout → Install Dependencies → Run Tests → Build Docker Image
```

| Stage                | Purpose                                        |
|----------------------|------------------------------------------------|
| Checkout             | Pull latest code from Git                      |
| Install Dependencies | `pip install -r requirements.txt`              |
| Run Tests            | `python test_routing.py`                       |
| Build Docker Image   | `docker build -t cost-optimized-ml-app:BUILD .`|

## Project Structure

```
├── app.py                  # Streamlit dashboard
├── router.py               # SmartRouter — automatic complexity routing
├── model_manager.py        # Loads and runs trained sklearn models
├── cost_simulator.py       # Simulated cost from latency profile
├── patients.py             # Patient profile management UI
├── models/
│   ├── model_a.pkl         # Logistic Regression
│   ├── model_b.pkl         # Random Forest
│   └── model_c.pkl         # Gradient Boosting
├── patients.json           # Saved patient profiles
├── latency_profile.json    # Measured inference latencies
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container definition
├── .dockerignore           # Docker build exclusions
├── Jenkinsfile             # CI pipeline definition
├── test_routing.py         # Automated routing & prediction tests
└── .streamlit/config.toml  # Streamlit theme
```

## Tech Stack

- Python 3.13
- Streamlit 1.64.0
- scikit-learn 1.8.0
- Docker
- Jenkins (CI)
