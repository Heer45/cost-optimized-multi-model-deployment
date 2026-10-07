import urllib.request, json 
import json 
import os 
import random 
from sklearn.datasets import load_breast_cancer 
 
PATIENTS_FILE = 'patients.json' 
 
def load_patients(): 
    if os.path.exists(PATIENTS_FILE): 
        with open(PATIENTS_FILE, 'r') as f: 
            try: 
                return json.load(f) 
            except: 
                return {} 
    return {} 
 
def save_patients(patients_dict): 
    with open(PATIENTS_FILE, 'w') as f: 
        json.dump(patients_dict, f, indent=4) 
 
@st.cache_data 
def get_dataset_info(): 
    data = load_breast_cancer() 
    feature_names = list(data.feature_names) 
    mean_group = feature_names[0:10] 
    error_group = feature_names[10:20] 
    worst_group = feature_names[20:30] 
    return feature_names, data.data, mean_group, error_group, worst_group 
 
def render_patients_page(): 
    st.title("Patient Profiles") 
    st.write("Manage patient 30-feature numerical vectors here. Later pages will simply pull from these profiles without duplicate typing entirely.") 
 
    patients = load_patients() 
    patient_names = list(patients.keys()) 
 
    feature_names, dataset_data, mean_group, error_group, worst_group = get_dataset_info() 
 
    # Navigation and Control System 
    if "patient_mode" not in st.session_state: 
        st.session_state.patient_mode = "create" if not patient_names else "edit" 
 
    def set_create(): 
        st.session_state.patient_mode = "create" 
 
    def set_edit(): 
        st.session_state.patient_mode = "edit" 
 
    col1, col2 = st.columns(2) 
    with col1: 
        st.write("") # subtle alignment 
        st.button("+ Create New Patient", on_click=set_create) 
 
    with col2: 
        if patient_names: 
            selected_option = st.selectbox( 
                "Select Existing Patient:", 
                patient_names, 
                key="patient_selector", 
                on_change=set_edit 
            ) 
        else: 
            selected_option = None 
 
    st.markdown("---") 
 
    is_new = (st.session_state.patient_mode == "create") or not patient_names 
 
    if is_new: 
        st.subheader("Create New Patient Profile") 
        patient_name = st.text_input("Patient Name (e.g. Patient 1)", value=f"Patient {len(patients) + 1}") 
 
        random_row_index = random.randint(0, len(dataset_data) - 1) 
        sample_row = dataset_data[random_row_index].tolist() 
        current_values = dict(zip(feature_names, sample_row)) 
    else: 
        st.subheader(f"Edit Profile: {selected_option}") 
        patient_name = selected_option 
        current_values = patients[selected_option] 
 
    def safe_float(v): 
        try: return float(v) 
        except: return 0.0 
 
    with st.form("patient_form"): 
        with st.expander(" Mean Measurements", expanded=True): 
            cols = st.columns(2) 
            inputs_mean = {} 
            for i, feature in enumerate(mean_group): 
                val = safe_float(current_values.get(feature, 0.0)) 
                inputs_mean[feature] = cols[i %% 2].number_input(feature.title(), value=val, format="%%.6f", step=0.1) 
 
        with st.expander(" Standard Error", expanded=False): 
            cols = st.columns(2) 
            inputs_error = {} 
            for i, feature in enumerate(error_group): 
                val = safe_float(current_values.get(feature, 0.0)) 
                inputs_error[feature] = cols[i %% 2].number_input(feature.title(), value=val, format="%%.6f", step=0.01) 
 
        with st.expander(" Worst Measurements", expanded=False): 
            cols = st.columns(2) 
            inputs_worst = {} 
            for i, feature in enumerate(worst_group): 
                val = safe_float(current_values.get(feature, 0.0)) 
                inputs_worst[feature] = cols[i %% 2].number_input(feature.title(), value=val, format="%%.6f", step=0.1) 
 
        submitted = st.form_submit_button("Save Patient") 
 
        if submitted: 
            if not patient_name.strip(): 
                st.error("Error: Patient name cannot be completely empty.") 
            else: 
                new_profile = {} 
                new_profile.update(inputs_mean) 
                new_profile.update(inputs_error) 
                new_profile.update(inputs_worst) 
 
                if len(new_profile) != 30: 
                    st.error("Error: Vector failed size validation (Expected 30 fields).") 
                else: 
                    patients[patient_name.strip()] = new_profile 
                    save_patients(patients) 
                    st.success(f"Successfully saved profile vector for {patient_name.strip()}!") 
                    st.rerun() 
with open('patients.py', 'w', encoding='utf-8') as f: 
    f.write(patient_py_content) 
