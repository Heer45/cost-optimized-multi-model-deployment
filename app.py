import json
import os
import time
from typing import cast

import numpy as np
import streamlit as st
from textwrap import dedent
from sklearn.datasets import load_breast_cancer
from sklearn.utils import Bunch

from cost_simulator import CostSimulator
from model_manager import ModelManager
from router import SmartRouter

# Jenkins automatic build verification
# Jenkins automatic build verification
# Jenkins automatic build verification - test 2
# Jenkins automatic build verification - test 2
# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Cost-Optimized Multi-Model Deployment",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATIENTS_FILE = os.path.join(BASE_DIR, "patients.json")
LATENCY_PROFILE = os.path.join(BASE_DIR, "latency_profile.json")

print("hello, world!")
# ============================================================
# FEATURE INFORMATION
# ============================================================

FEATURE_ORDER = [
    "mean radius",
    "mean texture",
    "mean perimeter",
    "mean area",
    "mean smoothness",
    "mean compactness",
    "mean concavity",
    "mean concave points",
    "mean symmetry",
    "mean fractal dimension",
    "radius error",
    "texture error",
    "perimeter error",
    "area error",
    "smoothness error",
    "compactness error",
    "concavity error",
    "concave points error",
    "symmetry error",
    "fractal dimension error",
    "worst radius",
    "worst texture",
    "worst perimeter",
    "worst area",
    "worst smoothness",
    "worst compactness",
    "worst concavity",
    "worst concave points",
    "worst symmetry",
    "worst fractal dimension",
]


FEATURE_GROUPS = {
    "Mean Measurements": FEATURE_ORDER[0:10],
    "Standard Error": FEATURE_ORDER[10:20],
    "Worst Measurements": FEATURE_ORDER[20:30],
}


# ============================================================
# CUSTOM CSS
# ============================================================

st.html(
    dedent("""
    <style>

    .main {
        background-color: #f6f8fb;
    }

    .block-container {
        padding-top: 4rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    .dashboard-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #172033;
        margin-bottom: 0.2rem;
    }

    .dashboard-subtitle {
        color: #667085;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 650;
        color: #172033;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
    }

    .info-card {
        background: white;
        border-radius: 16px;
        padding: 1.2rem 1.3rem;
        border: 1px solid #e7eaf0;
        box-shadow: 0 3px 12px rgba(20, 30, 50, 0.05);
        margin-bottom: 1rem;
    }

    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 1.1rem;
        border: 1px solid #e7eaf0;
        box-shadow: 0 3px 12px rgba(20, 30, 50, 0.05);
        min-height: 115px;
    }

    .metric-label {
        color: #667085;
        font-size: 0.85rem;
        margin-bottom: 0.35rem;
    }

    .metric-value {
        color: #172033;
        font-size: 1.55rem;
        font-weight: 700;
    }

    .routing-card {
        background: #eef7f2;
        border: 1px solid #cce6d8;
        border-radius: 16px;
        padding: 1.2rem 1.3rem;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }

    .routing-title {
        color: #24563f;
        font-size: 0.85rem;
        font-weight: 650;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .routing-model {
        color: #183d2c;
        font-size: 1.55rem;
        font-weight: 750;
        margin-top: 0.2rem;
    }

    .routing-description {
        color: #4d6b5b;
        font-size: 0.9rem;
        margin-top: 0.35rem;
    }

    .cost-selected {
        background: #eef7f2;
        border: 1px solid #cce6d8;
        border-radius: 12px;
        padding: 0.8rem;
    }

    .cost-normal {
        background: #ffffff;
        border: 1px solid #e7eaf0;
        border-radius: 12px;
        padding: 0.8rem;
    }

    </style>
    """),
)


# ============================================================
# DATA / OBJECT LOADERS
# ============================================================


@st.cache_resource
def get_model_manager():
    manager = ModelManager(os.path.join(BASE_DIR, "models"))
    manager.load_models()
    return manager




def get_router():
    return SmartRouter()


@st.cache_resource
def get_cost_simulator():
    return CostSimulator(
        baseline_cost=0.01,
        profile_path=LATENCY_PROFILE,
    )


def load_patients():
    """Load locally saved patient profiles."""

    if not os.path.exists(PATIENTS_FILE):
        return {}

    try:
        with open(PATIENTS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, dict):
            return data

        return {}

    except (json.JSONDecodeError, OSError):
        return {}


def save_patients(patients):
    """Save patient profiles locally."""

    with open(PATIENTS_FILE, "w", encoding="utf-8") as file:
        json.dump(patients, file, indent=4)


# ============================================================
# PATIENT FEATURE HELPERS
# ============================================================


def get_default_patient_features():
    """
    Get one genuine sample from the sklearn Breast Cancer dataset.

    This is used only to prefill a newly created patient profile.
    """

    data = cast(Bunch, load_breast_cancer(return_X_y=False))

    sample = data.data[0]

    return {
        feature_name: float(value)
        for feature_name, value in zip(FEATURE_ORDER, sample)
    }


def build_feature_vector(patient):
    """Convert a patient dictionary into the exact 30-feature order."""

    values = []

    for feature_name in FEATURE_ORDER:
        values.append(float(patient.get(feature_name, 0.0)))

    return [values]


# ============================================================
# PATIENT PAGE
# ============================================================


def render_feature_editor(patient):
    """
    Display all 30 patient features grouped into three sections.
    """

    updated_patient = dict(patient)

    for group_name, features in FEATURE_GROUPS.items():

        st.html(
            f'<div class="section-title">{group_name}</div>',
        )

        columns = st.columns(2)

        for index, feature_name in enumerate(features):

            column = columns[index % 2]

            with column:
                updated_patient[feature_name] = st.number_input(
                    feature_name.title(),
                    value=float(patient.get(feature_name, 0.0)),
                    format="%.6f",
                    key=f"feature_{feature_name.replace(' ', '_')}",
                )

    return updated_patient


def render_patients_page():
    st.html(
        '<div class="dashboard-title">Patients</div>',
    )

    st.html(
        '<div class="dashboard-subtitle">'
        "Create and manage local patient profiles used for model inference."
        "</div>",
    )

    patients = load_patients()

    # --------------------------------------------------------
    # CREATE NEW PATIENT
    # --------------------------------------------------------

    if st.button("+ Create New Patient", use_container_width=False):

        st.session_state.patient_mode = "create"
        st.session_state.edit_patient_name = None

        st.session_state.new_patient_data = (
            get_default_patient_features()
        )

        st.rerun()

    # --------------------------------------------------------
    # CREATE MODE
    # --------------------------------------------------------

    if st.session_state.get("patient_mode") == "create":

        st.html(
            '<div class="section-title">Create Patient</div>',
        )

        patient_name = st.text_input(
            "Patient Name",
            placeholder="Enter patient name",
        )

        patient_data = st.session_state.get(
            "new_patient_data",
            get_default_patient_features(),
        )

        patient_data = render_feature_editor(patient_data)

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Save Patient",
                type="primary",
                use_container_width=True,
            ):

                if not patient_name.strip():

                    st.error("Please enter a patient name.")

                elif patient_name.strip() in patients:

                    st.error(
                        "A patient with this name already exists."
                    )

                else:

                    patients[patient_name.strip()] = patient_data

                    save_patients(patients)

                    st.session_state.patient_mode = "view"

                    st.success(
                        f"Patient '{patient_name.strip()}' created."
                    )

                    st.rerun()

        with col2:

            if st.button(
                "Cancel",
                use_container_width=True,
            ):

                st.session_state.patient_mode = "view"
                st.rerun()

        return

    # --------------------------------------------------------
    # EXISTING PATIENTS
    # --------------------------------------------------------

    if not patients:

        st.info(
            "No patients created yet. Click '+ Create New Patient' "
            "to create the first profile."
        )

        return

    st.html(
        '<div class="section-title">Existing Patients</div>',
    )

    patient_names = list(patients.keys())

    selected_patient = st.selectbox(
        "Select Patient",
        patient_names,
    )

    patient_data = patients[selected_patient]

    st.html(
        '<div class="section-title">Patient Features</div>',
    )

    updated_patient = render_feature_editor(patient_data)

    if st.button(
        "Save Changes",
        type="primary",
        use_container_width=False,
    ):

        patients[selected_patient] = updated_patient

        save_patients(patients)

        st.success(
            f"Changes saved for {selected_patient}."
        )

        st.rerun()


# ============================================================
# DASHBOARD
# ============================================================



def render_dashboard():
    st.html(
        '<div class="dashboard-title">'
        "Cost-Optimized Multi-Model Deployment"
        "</div>",
    )

    st.html(
        '<div class="dashboard-subtitle">'
        "Automatically route each request to an appropriate ML model "
        "while tracking inference latency and simulated cost."
        "</div>",
    )

    patients = load_patients()

    # --------------------------------------------------------
    # PATIENT SELECTION
    # --------------------------------------------------------

    st.html(
        '<div class="section-title">Select Patient</div>',
    )

    if not patients:

        st.warning(
            "No patient profiles available. "
            "Go to the Patients page and create a patient first."
        )

        return

    patient_names = list(patients.keys())

    selected_patient_name = st.selectbox(
        "Patient",
        patient_names,
        label_visibility="collapsed",
    )

    selected_patient = patients[selected_patient_name]

    st.html(
        dedent(f"""
        <div class="info-card">
            <strong>{selected_patient_name}</strong><br>
            <span style="color:#667085;">
                Patient profile loaded. The 30 feature values will be
                automatically analyzed by the Smart Router.
            </span>
        </div>
        """),
    )

    # --------------------------------------------------------
    # RUN INFERENCE
    # --------------------------------------------------------

    run_inference = st.button(
        "⚡ RUN INFERENCE",
        type="primary",
        use_container_width=True,
    )

    if not run_inference:
        st.info(
            "Click 'RUN INFERENCE' to send this patient's data "
            "through the automatic routing system."
        )

        return

    # --------------------------------------------------------
    # BUILD INPUT
    # --------------------------------------------------------

    input_data = build_feature_vector(selected_patient)

    # --------------------------------------------------------
    # LOAD SYSTEM COMPONENTS
    # --------------------------------------------------------

    try:

        router = get_router()
        model_manager = get_model_manager()
        cost_simulator = get_cost_simulator()

    except Exception as error:

        st.error(
            f"Unable to initialize the deployment system: {error}"
        )

        return

    # --------------------------------------------------------
    # AUTOMATIC ROUTING
    # --------------------------------------------------------

    try:

        routing_decision = router.route(input_data)

    except Exception as error:
        import traceback
        st.error(f"Automatic routing failed: {error}")
        st.error(traceback.format_exc())
        return

    complexity = routing_decision["complexity"]
    complexity_score = routing_decision["complexity_score"]
    selected_model = routing_decision["selected_model"]
    routing_reason = routing_decision["reason"]

    # --------------------------------------------------------
    # ACTUAL MODEL INFERENCE
    # --------------------------------------------------------

    try:

        start_time = time.perf_counter()

        prediction = model_manager.predict(
            selected_model,
            input_data,
        )

        end_time = time.perf_counter()

        actual_latency_ms = (
            end_time - start_time
        ) * 1000

    except Exception as error:

        st.error(
            f"Model inference failed: {error}"
        )

        return

    # --------------------------------------------------------
    # EXTRACT PREDICTION
    # --------------------------------------------------------

    try:

        prediction_value = int(
            np.asarray(prediction).flatten()[0]
        )

    except Exception:

        prediction_value = prediction

    if prediction_value == 0:
        prediction_label = "Malignant"
    elif prediction_value == 1:
        prediction_label = "Benign"
    else:
        prediction_label = str(prediction_value)

    # --------------------------------------------------------
    # COST CALCULATION
    # --------------------------------------------------------

    try:

        cost_result = cost_simulator.calculate_model_cost(
            selected_model
        )

        selected_cost = float(
            cost_result["simulated_cost"]
        )

    except Exception as error:

        st.error(
            f"Cost calculation failed: {error}"
        )

        return

    # --------------------------------------------------------
    # COST PROFILE
    # --------------------------------------------------------

    try:

        cost_profile = cost_simulator.get_cost_profile()

    except Exception:

        cost_profile = {}

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    st.html(
        '<div class="section-title">Automatic Routing Result</div>',
    )

    st.html(
        dedent(f"""
        <div class="routing-card">

            <div class="routing-title">
                Automatically Selected Model
            </div>

            <div class="routing-model">
                {selected_model}
            </div>

            <div class="routing-description">
                {routing_reason}
            </div>

        </div>
        """),
    )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.html(
            dedent(f"""
            <div class="metric-card">
                <div class="metric-label">
                    Detected Complexity
                </div>
                <div class="metric-value">
                    {complexity}
                </div>
            </div>
            """),
        )

    with col2:

        st.html(
            dedent(f"""
            <div class="metric-card">
                <div class="metric-label">
                    Complexity Score
                </div>
                <div class="metric-value">
                    {complexity_score:.2f}
                </div>
            </div>
            """),
        )

    with col3:

        st.html(
            dedent(f"""
            <div class="metric-card">
                <div class="metric-label">
                    Inference Latency
                </div>
                <div class="metric-value">
                    {actual_latency_ms:.2f} ms
                </div>
            </div>
            """),
        )

    with col4:

        st.html(
            dedent(f"""
            <div class="metric-card">
                <div class="metric-label">
                    Simulated Cost
                </div>
                <div class="metric-value">
                    ₹{selected_cost:.4f}
                </div>
            </div>
            """),
        )

    # --------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------

    st.html(
        '<div class="section-title">Prediction</div>',
    )

    prediction_col1, prediction_col2 = st.columns(2)

    with prediction_col1:

        st.html(
            dedent(f"""
            <div class="info-card">
                <div class="metric-label">
                    Patient
                </div>

                <div class="metric-value">
                    {selected_patient_name}
                </div>
            </div>
            """),
        )

    with prediction_col2:

        st.html(
            dedent(f"""
            <div class="info-card">
                <div class="metric-label">
                    Model Prediction
                </div>

                <div class="metric-value">
                    {prediction_label}
                </div>
            </div>
            """),
        )

    # --------------------------------------------------------
    # COST COMPARISON
    # --------------------------------------------------------

    st.html(
        '<div class="section-title">Model Cost Comparison</div>',
    )

    st.caption(
        "Costs shown below are simulated benchmark costs based "
        "on measured inference latency. They are not real cloud prices."
    )

    comparison_columns = st.columns(3)

    model_names = [
        "Model A",
        "Model B",
        "Model C",
    ]

    for column, model_name in zip(
        comparison_columns,
        model_names,
    ):

        with column:

            if model_name == selected_model:
                card_class = "cost-selected"
                status = "SELECTED BY ROUTER"
            else:
                card_class = "cost-normal"
                status = "ALTERNATIVE"

            model_cost = 0.0

            try:

                if model_name in cost_profile:

                    profile = cost_profile[model_name]

                    if isinstance(profile, dict):

                        model_cost = float(
                            profile.get(
                                "simulated_cost",
                                profile.get("cost", 0.0),
                            )
                        )

                    else:

                        model_cost = float(profile)

                else:

                    model_cost_result = (
                        cost_simulator.calculate_model_cost(
                            model_name
                        )
                    )

                    model_cost = float(
                        model_cost_result["simulated_cost"]
                    )

            except Exception:

                model_cost = 0.0

            st.html(
                dedent(f"""
                <div class="{card_class}">
                    <div style="
                        color:#667085;
                        font-size:0.82rem;
                    ">
                        {status}
                    </div>

                    <div style="
                        font-size:1.2rem;
                        font-weight:700;
                        color:#172033;
                        margin-top:0.25rem;
                    ">
                        {model_name}
                    </div>

                    <div style="
                        font-size:1.35rem;
                        font-weight:700;
                        color:#172033;
                        margin-top:0.35rem;
                    ">
                        ₹{model_cost:.4f}
                    </div>
                </div>
                """),
            )

    # --------------------------------------------------------
    # ROUTING EXPLANATION
    # --------------------------------------------------------

    st.html(
        '<div class="section-title">Why Was This Model Selected?</div>',
    )

    st.html(
        dedent(f"""
        <div class="info-card">

            <strong>Automatic decision:</strong><br><br>

            The patient's 30 input features were analyzed by the
            Smart Router.

            <br><br>

            <strong>Complexity score:</strong>
            {complexity_score:.2f}

            <br><br>

            <strong>Detected complexity:</strong>
            {complexity}

            <br><br>

            <strong>Selected model:</strong>
            {selected_model}

            <br><br>

            <span style="color:#667085;">
                The user does not manually select the complexity or
                model. The routing decision is made automatically
                before inference.
            </span>

        </div>
        """),
    )


# ============================================================
# PLACEHOLDER PAGES
# ============================================================


def render_model_comparison():

    st.html(
        '<div class="dashboard-title">Model Comparison</div>',
    )

    st.html(
        '<div class="dashboard-subtitle">'
        "Compare the three deployed models."
        "</div>",
    )

    try:

        cost_simulator = get_cost_simulator()

        cost_profile = cost_simulator.get_cost_profile()

        rows = []

        for model_name in [
            "Model A",
            "Model B",
            "Model C",
        ]:

            profile = cost_profile.get(model_name, {})

            if isinstance(profile, dict):

                rows.append(
                    {
                        "Model": model_name,
                        "Latency (ms)": profile.get(
                            "latency_ms",
                            profile.get("latency", "-"),
                        ),
                        "Simulated Cost (₹)": profile.get(
                            "simulated_cost",
                            profile.get("cost", "-"),
                        ),
                    }
                )

        if rows:
            st.dataframe(
                rows,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No model profile data available.")

    except Exception as error:

        st.error(
            f"Unable to load model comparison: {error}"
        )


def render_cost_analytics():

    st.html(
        '<div class="dashboard-title">Cost Analytics</div>',
    )

    st.html(
        '<div class="dashboard-subtitle">'
        "Analyze the simulated inference cost of each model."
        "</div>",
    )

    try:
        cost_simulator = get_cost_simulator()
        cost_profile = cost_simulator.get_cost_profile()
    except Exception as e:
        st.error(f"Failed to load cost data: {e}")
        return

    if not cost_profile or "Model A" not in cost_profile:
        st.warning("Cost profile is incomplete.")
        return

    # Calculate Summaries
    model_a_cost = cost_profile["Model A"]["simulated_cost"]
    
    most_expensive_model = max(cost_profile.keys(), key=lambda k: cost_profile[k]["simulated_cost"])
    highest_ratio = max(cost_profile[k]["latency_ratio"] for k in cost_profile.keys())
    num_models = len(cost_profile)

    # Render summary cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.html(
            dedent(f'''
            <div class="metric-card">
                <div class="metric-label">
                    Baseline Cost
                </div>
                <div class="metric-value">
                    ₹{model_a_cost:.4f}
                </div>
            </div>
            ''')
        )

    with col2:
        st.html(
            dedent(f'''
            <div class="metric-card">
                <div class="metric-label">
                    Most Expensive Model
                </div>
                <div class="metric-value">
                    {most_expensive_model}
                </div>
            </div>
            ''')
        )

    with col3:
        st.html(
            dedent(f'''
            <div class="metric-card">
                <div class="metric-label">
                    Highest Cost Ratio
                </div>
                <div class="metric-value">
                    {highest_ratio:.2f}×
                </div>
            </div>
            ''')
        )

    with col4:
        st.html(
            dedent(f'''
            <div class="metric-card">
                <div class="metric-label">
                    Models Analyzed
                </div>
                <div class="metric-value">
                    {num_models}
                </div>
            </div>
            ''')
        )

    import pandas as pd

    st.html(
        '<div class="section-title">Model Cost Comparison</div>',
    )
    
    chart_data = pd.DataFrame(
        [
            {"Model": m, "Simulated Cost (₹)": cost_profile[m]["simulated_cost"]} 
            for m in cost_profile
        ]
    ).set_index("Model")
    
    st.bar_chart(chart_data)

    table_data = []
    for m in cost_profile:
        table_data.append({
            "Model": m,
            "Latency (ms)": f"{cost_profile[m]['latency_ms']:.2f} ms",
            "Relative Cost": f"{cost_profile[m]['latency_ratio']:.2f}×",
            "Simulated Cost (₹)": f"₹{cost_profile[m]['simulated_cost']:.4f}"
        })
    st.table(pd.DataFrame(table_data))

    st.html(
        '<div class="section-title">Simulated Cost Savings</div>',
    )
    
    for m in cost_profile:
        if m == "Model A":
            continue
            
        savings_info = cost_simulator.calculate_savings("Model A", m)
        expensive_cost = cost_profile[m]["simulated_cost"]
        saving_amt = savings_info["savings"]
        pct_saving = savings_info["savings_percentage"]
        
        st.html(
            dedent(f'''
            <div class="info-card">
                <strong>Model A vs {m}</strong><br>
                <div style="margin-top:0.5rem; color:#172033;">
                    Cost of {m}: ₹{expensive_cost:.4f} <br>
                    Cost of Model A: ₹{model_a_cost:.4f} <br>
                    <strong>Simulated savings per request:</strong> ₹{saving_amt:.4f} <br>
                    <strong>Percentage difference:</strong> {pct_saving:.1f}%
                </div>
            </div>
            ''')
        )
        
    st.html(
        '<div class="section-title">How Cost Is Calculated</div>',
    )
    
    st.html(
        dedent('''
        <div class="info-card" style="color:#172033;">
            Model A is used as the baseline.<br><br>
            
            <strong>Latency ratio:</strong><br>
            model latency / Model A latency<br><br>
            
            <strong>Simulated cost:</strong><br>
            baseline cost × latency ratio<br><br>
            
            <em>Example:</em><br>
            If a model takes approximately 10× the baseline latency, 
            its simulated cost is approximately 10× the baseline cost.<br><br>
            
            <span style="color:#667085; font-size:0.85rem;">
                This is a simulated benchmark-based cost model for the educational 
                prototype and does not represent actual cloud provider pricing.
            </span>
        </div>
        ''')
    )


def render_request_history():

    st.html(
        '<div class="dashboard-title">Request History</div>',
    )

    st.html(
        '<div class="dashboard-subtitle">'
        "Inference request history."
        "</div>",
    )

    st.info(
        "Request history storage will be added in a later phase."
    )


def render_how_it_works():

    st.html(
        '<div class="dashboard-title">How It Works</div>',
    )

    st.html(
        '<div class="dashboard-subtitle">'
        "Architecture of the cost-optimized multi-model deployment system."
        "</div>",
    )

    st.html(
        dedent("""
        <div class="info-card">

        <h3>1. Patient Request</h3>

        A patient profile containing 30 numerical features is selected.

        <br><br>

        ↓

        <br><br>

        <h3>2. Automatic Complexity Analysis</h3>

        The Smart Router calculates an input-complexity score by
        measuring how far the feature values deviate from the
        training-data distribution.

        <br><br>

        ↓

        <br><br>

        <h3>3. Smart Routing</h3>

        <strong>Simple → Model A</strong><br>
        <strong>Medium → Model B</strong><br>
        <strong>Complex → Model C</strong>

        <br><br>

        ↓

        <br><br>

        <h3>4. Actual Inference</h3>

        The selected trained model performs the prediction.

        <br><br>

        ↓

        <br><br>

        <h3>5. Cost & Latency Tracking</h3>

        The system measures actual inference latency and calculates
        a simulated cost based on the model's benchmark profile.

        <br><br>

        ↓

        <br><br>

        <h3>6. Dashboard</h3>

        The final prediction, selected model, complexity,
        latency and cost are displayed.

        </div>
        """),
    )


# ============================================================
# SIDEBAR
# ============================================================


def render_sidebar():

    st.sidebar.html(
        dedent("""
        <div style="
            font-size:1.35rem;
            font-weight:750;
            margin-bottom:0.2rem;
            color:#172033;
        ">
            ⚡ ModelDeploy
        </div>

        <div style="
            font-size:0.8rem;
            color:#667085;
            margin-bottom:1.2rem;
        ">
            Cost-Optimized ML Deployment
        </div>
        """),
    )

    page = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Patients",
            "Model Comparison",
            "Cost Analytics",
            "Request History",
            "How It Works",
        ],
    )

    st.sidebar.markdown("---")

    st.sidebar.caption(
        "Local educational prototype"
    )

    return page


# ============================================================
# MAIN APPLICATION
# ============================================================


def main():

    # Initialize session state
    if "patient_mode" not in st.session_state:
        st.session_state.patient_mode = "view"

    page = render_sidebar()

    if page == "Dashboard":

        render_dashboard()

    elif page == "Patients":

        render_patients_page()

    elif page == "Model Comparison":

        render_model_comparison()

    elif page == "Cost Analytics":

        render_cost_analytics()

    elif page == "Request History":

        render_request_history()

    elif page == "How It Works":

        render_how_it_works()


if __name__ == "__main__":
    main()