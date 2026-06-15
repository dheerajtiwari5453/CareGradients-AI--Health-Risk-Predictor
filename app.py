"""Entry point for the CareGradients AI Streamlit application.

Provides a premium UI for patient risk assessment, database interaction,
and visual analytics.
"""
import streamlit as st
import pandas as pd
import numpy as np
import io

# Setup Streamlit page configuration
st.set_page_config(
    page_title="CareGradients AI -Health Risk Predictor",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.predictor import HealthRiskPredictor
from src.styles import apply_custom_styles, draw_card, draw_delta_card
from src.explainers import run_sensitivity_analysis, generate_sensitivity_plot
from src.visualizations import generate_radar_chart
from src.reports import generate_html_report
from src.database import save_record, load_records, delete_record, init_db

# Initialize custom CSS styles
apply_custom_styles()

@st.cache_resource
def get_prediction_pipeline():
    """
    Returns the cached instance of the prediction pipeline.
    """
    return HealthRiskPredictor()

try:
    predictor = get_prediction_pipeline()
except Exception as e:
    st.error(f"Prediction Pipeline initialization failed. Details: {e}")
    st.stop()

# Initialize Database
init_db()

# ==========================================
# SIDEBAR NAVIGATION & PORTAL ROUTING
# ==========================================
st.sidebar.markdown("# 🩺 CareGradients AI")
st.sidebar.markdown("<small style='color:#94a3b8;'>Clinical Decision Support Engine</small>", unsafe_allow_html=True)
st.sidebar.markdown("---")

portal_view = st.sidebar.radio(
    "Clinical Portals",
    [
        "🖥️ Individual Diagnostic Suite",
        "⚖️ Intervention Delta Analyzer",
        "📊 Batch Processing Portal",
        "🗃️ Clinical Registry Database",
        "📘 Targets & Guidelines"
    ]
)

st.sidebar.markdown("---")

# ==========================================
# PORTAL 1: INDIVIDUAL DIAGNOSTIC SUITE
# ==========================================
if portal_view == "🖥️ Individual Diagnostic Suite":
    st.markdown("## 🖥️ Patient Diagnostic Suite")
    st.write("Perform detailed clinical assessments, view risk radar footprints, and save records.")
    st.write("---")
    
    # Sidebar clinical inputs
    st.sidebar.markdown("### 👤 Demographics & Vitals")
    age = st.sidebar.slider("Age (years)", 18, 90, 45)
    gender = st.sidebar.selectbox("Assigned Gender at Birth", ["Female", "Male"])
    BMI = st.sidebar.slider("Body Mass Index (BMI)", 15.0, 45.0, 26.5, step=0.1)
    
    systolic_bp = st.sidebar.slider("Systolic BP (mmHg)", 90, 200, 120)
    diastolic_bp = st.sidebar.slider("Diastolic BP (mmHg)", 60, 120, 80)
    cholesterol = st.sidebar.slider("Total Cholesterol (mg/dL)", 100, 400, 190)
    glucose = st.sidebar.slider("Fasting Glucose (mg/dL)", 60, 300, 95)
    
    st.sidebar.markdown("### 🚬 Behavior & Lifestyle")
    smoking = st.sidebar.selectbox("Current Smoker", ["No", "Yes"])
    physical_activity = st.sidebar.selectbox("Physically Active (150+ min/wk)", ["Yes", "No"])
    
    # Advanced flags in sidebar
    with st.sidebar.expander("🛠️ Advanced Clinical Settings"):
        cigs_per_day = 0
        if smoking == "Yes":
            cigs_per_day = st.slider("Cigarettes Per Day", 0, 60, 10)
        bp_meds = 1.0 if st.checkbox("Taking BP Medications") else 0.0
        prevalent_hypertension = 1.0 if st.checkbox("Hypertension History") else 0.0
        heart_rate = st.slider("Resting Heart Rate (BPM)", 40, 140, 72)
        alcohol = 1.0 if st.checkbox("Consumes Alcohol") else 0.0
        heavy_alcohol = 1.0 if st.checkbox("Heavy Drinker (14+ drinks/wk)") else 0.0
        prevalent_stroke = 1.0 if st.checkbox("Stroke History") else 0.0
        heart_disease_history = 1.0 if st.checkbox("Cardiovascular History") else 0.0
        diabetes_history = 1.0 if st.checkbox("Diabetes History") else 0.0
        height = st.slider("Height (cm)", 120, 220, 170)
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=180.0, value=float(round(BMI * ((height/100.0)**2), 1)))

    # Process categories & dictionary profile
    bmi_cat_str = (
        "underweight" if BMI < 18.5 else
        "normal" if BMI < 25.0 else
        "overweight" if BMI < 30.0 else
        "obese"
    )
    
    patient_profile = {
        "age": age, "age_decade": int(age // 10), "gender": 1.0 if gender == "Male" else 0.0,
        "BMI": BMI, "BMI_cat": bmi_cat_str, "systolic_bp": systolic_bp, "diastolic_bp": diastolic_bp,
        "pulse_pressure": systolic_bp - diastolic_bp, "cholesterol": cholesterol, "glucose": glucose,
        "smoking": 1.0 if smoking == "Yes" else 0.0, "physical_activity": 1.0 if physical_activity == "Yes" else 0.0,
        "cigs_per_day": float(cigs_per_day), "bp_meds": float(bp_meds), "prevalent_hypertension": float(prevalent_hypertension),
        "heart_rate": float(heart_rate), "alcohol": float(alcohol), "heavy_alcohol": float(heavy_alcohol),
        "prevalent_stroke": float(prevalent_stroke), "heart_disease_history": float(heart_disease_history),
        "diabetes_history": float(diabetes_history), "height": float(height), "weight": float(weight),
        "ap_low": float(diastolic_bp),
        # missing flags
        "age_missing": 0.0, "gender_missing": 0.0, "BMI_missing": 0.0, "BMI_cat_missing": 0.0,
        "systolic_bp_missing": 0.0, "diastolic_bp_missing": 0.0, "pulse_pressure_missing": 0.0,
        "cholesterol_missing": 0.0, "glucose_missing": 0.0, "smoking_missing": 0.0,
        "physical_activity_missing": 0.0, "cigs_per_day_missing": 0.0, "bp_meds_missing": 0.0,
        "prevalent_hypertension_missing": 0.0, "heart_rate_missing": 0.0, "alcohol_missing": 0.0,
        "heavy_alcohol_missing": 0.0, "prevalent_stroke_missing": 0.0, "heart_disease_history_missing": 0.0,
        "diabetes_history_missing": 0.0, "height_missing": 0.0, "weight_missing": 0.0, "ap_low_missing": 0.0
    }

    # Run predictions
    heart_p = predictor.predict_risk(patient_profile, "heart")
    diab_p = predictor.predict_risk(patient_profile, "diabetes")
    stroke_p = predictor.predict_risk(patient_profile, "stroke")
    composite_p = predictor.calculate_composite_risk(heart_p, diab_p, stroke_p)

    # UI Split Layout
    left_col, right_col = st.columns([4, 5])
    
    with left_col:
        # Composite score Dial
        st.markdown(
            f"""
            <div class="composite-panel">
                <div class="composite-title">COMPOSITE RISK INDEX</div>
                <div class="composite-val">{composite_p}%</div>
                <p style="margin: 0; font-size: 13px; color: #64748b;">Combined Cardiovascular, Metabolic, and Cerebrovascular Risk</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Individual cards
        st.markdown("#### Individual Risks")
        draw_card("Cardiovascular Risk", heart_p, "color-heart")
        draw_card("Metabolic Risk (Diabetes)", diab_p, "color-diabetes")
        draw_card("Cerebrovascular Risk (Stroke)", stroke_p, "color-stroke")
        
        # Save assessment Form
        st.write("---")
        st.markdown("#### 💾 Save or Export Assessment")
        
        with st.form("registry_form", clear_on_submit=False):
            pat_name = st.text_input("Patient Name", placeholder="e.g. Dheeraj Tiwari")
            pat_id = st.text_input("Patient ID / HRN", placeholder="e.g. PT-9824")
            submit_btn = st.form_submit_button("Save & Generate Report")
            
            if submit_btn:
                if not pat_name or not pat_id:
                    st.warning("Please fill in Patient Name and Patient ID to register.")
                else:
                    save_record(
                        pat_id, pat_name, age, gender, BMI, systolic_bp, diastolic_bp,
                        cholesterol, glucose, smoking, physical_activity,
                        heart_p*100, diab_p*100, stroke_p*100, composite_p
                    )
                    st.success(f"Assessment successfully logged in registry for patient: {pat_name}")
                    
                    # Generate report and save to session state for download outside the form
                    report_html = generate_html_report(pat_id, pat_name, patient_profile, heart_p, diab_p, stroke_p, composite_p)
                    st.session_state["last_assessment"] = report_html
                    st.session_state["last_patient_id"] = pat_id
                    st.session_state["saved_patient_name"] = pat_name

        # Expose download button outside the form container
        if "last_assessment" in st.session_state:
            st.markdown("---")
            st.markdown(f"#### 📥 Export Clinical Report for {st.session_state['saved_patient_name']}")
            st.download_button(
                label="Download Clinical PDF/HTML",
                data=st.session_state["last_assessment"],
                file_name=f"Clinical_Report_{st.session_state['last_patient_id']}.html",
                mime="text/html"
            )

    with right_col:
        st.markdown("#### 📊 Diagnostic Footprint Visualizations")
        
        v_tab1, v_tab2 = st.tabs(["🗺️ Radar Footprint", "📈 Feature Sensitivity"])
        
        with v_tab1:
            radar_fig = generate_radar_chart(patient_profile, heart_p, diab_p, stroke_p)
            st.pyplot(radar_fig, clear_figure=True)
            st.caption("The blue dashed perimeter marks the ideal healthy benchmark threshold boundary.")
            
        with v_tab2:
            sens_disease = st.selectbox("Select Target for Sensitivity Chart", ["Heart Disease", "Diabetes Risk", "Stroke Probability"])
            map_keys = {"Heart Disease": "heart", "Diabetes Risk": "diabetes", "Stroke Probability": "stroke"}
            sens_key = map_keys[sens_disease]
            
            sens_records = run_sensitivity_analysis(predictor, patient_profile, sens_key)
            sens_fig = generate_sensitivity_plot(sens_records, sens_disease)
            st.pyplot(sens_fig, clear_figure=True)

# ==========================================
# PORTAL 2: INTERVENTION DELTA ANALYZER
# ==========================================
elif portal_view == "⚖️ Intervention Delta Analyzer":
    st.markdown("## ⚖️ Clinical Intervention Comparator")
    st.write("Model the impact of hypothetical clinical interventions (e.g. smoking cessation, pressure control) against base values.")
    st.write("---")
    
    # Input side-by-side forms
    f_col1, f_col2 = st.columns(2)
    
    with f_col1:
        st.markdown("### 🔴 Baseline Profile")
        b_age = st.number_input("Age", 18, 90, 45, key="b_age")
        b_gender = st.selectbox("Gender", ["Female", "Male"], key="b_gender")
        b_bmi = st.slider("BMI", 15.0, 45.0, 31.0, key="b_bmi")
        b_sys = st.slider("Systolic BP", 90, 200, 145, key="b_sys")
        b_dia = st.slider("Diastolic BP", 60, 120, 95, key="b_dia")
        b_chol = st.slider("Cholesterol", 100, 400, 240, key="b_chol")
        b_gluc = st.slider("Glucose", 60, 300, 115, key="b_gluc")
        b_smk = st.selectbox("Smoking", ["Yes", "No"], key="b_smk")
        b_act = st.selectbox("Physically Active", ["No", "Yes"], key="b_act")
        
    with f_col2:
        st.markdown("### 🟢 Intervention Goals")
        i_age = b_age # Age remains fixed
        i_gender = b_gender
        i_bmi = st.slider("Target BMI", 15.0, 45.0, float(b_bmi), key="i_bmi")
        i_sys = st.slider("Target Systolic BP", 90, 200, int(b_sys), key="i_sys")
        i_dia = st.slider("Target Diastolic BP", 60, 120, int(b_dia), key="i_dia")
        i_chol = st.slider("Target Cholesterol", 100, 400, int(b_chol), key="i_chol")
        i_gluc = st.slider("Target Glucose", 60, 300, int(b_gluc), key="i_gluc")
        i_smk = st.selectbox("Target Smoking Status", [b_smk, "Yes" if b_smk == "No" else "No"], key="i_smk")
        i_act = st.selectbox("Target Activity level", [b_act, "Yes" if b_act == "No" else "No"], key="i_act")
        
    # Helper to build profiles
    def build_profile(age, gender, BMI, sys, dia, chol, gluc, smk, act):
        cat = "underweight" if BMI < 18.5 else "normal" if BMI < 25.0 else "overweight" if BMI < 30.0 else "obese"
        return {
            "age": age, "age_decade": int(age // 10), "gender": 1.0 if gender == "Male" else 0.0,
            "BMI": BMI, "BMI_cat": cat, "systolic_bp": sys, "diastolic_bp": dia,
            "pulse_pressure": sys - dia, "cholesterol": chol, "glucose": gluc,
            "smoking": 1.0 if smk == "Yes" else 0.0, "physical_activity": 1.0 if act == "Yes" else 0.0,
            "cigs_per_day": 10.0 if smk == "Yes" else 0.0, "bp_meds": 0.0, "prevalent_hypertension": 0.0,
            "heart_rate": 72.0, "alcohol": 0.0, "heavy_alcohol": 0.0, "prevalent_stroke": 0.0,
            "heart_disease_history": 0.0, "diabetes_history": 0.0, "height": 170.0, "weight": 70.0, "ap_low": float(dia),
            "age_missing": 0.0, "gender_missing": 0.0, "BMI_missing": 0.0, "BMI_cat_missing": 0.0,
            "systolic_bp_missing": 0.0, "diastolic_bp_missing": 0.0, "pulse_pressure_missing": 0.0,
            "cholesterol_missing": 0.0, "glucose_missing": 0.0, "smoking_missing": 0.0,
            "physical_activity_missing": 0.0, "cigs_per_day_missing": 0.0, "bp_meds_missing": 0.0,
            "prevalent_hypertension_missing": 0.0, "heart_rate_missing": 0.0, "alcohol_missing": 0.0,
            "heavy_alcohol_missing": 0.0, "prevalent_stroke_missing": 0.0, "heart_disease_history_missing": 0.0,
            "diabetes_history_missing": 0.0, "height_missing": 0.0, "weight_missing": 0.0, "ap_low_missing": 0.0
        }
        
    profile_base = build_profile(b_age, b_gender, b_bmi, b_sys, b_dia, b_chol, b_gluc, b_smk, b_act)
    profile_target = build_profile(i_age, i_gender, i_bmi, i_sys, i_dia, i_chol, i_gluc, i_smk, i_act)
    
    # Calculate risks
    hb = predictor.predict_risk(profile_base, "heart")
    ht = predictor.predict_risk(profile_target, "heart")
    
    db = predictor.predict_risk(profile_base, "diabetes")
    dt = predictor.predict_risk(profile_target, "diabetes")
    
    sb = predictor.predict_risk(profile_base, "stroke")
    st_r = predictor.predict_risk(profile_target, "stroke")
    
    cb = predictor.calculate_composite_risk(hb, db, sb)
    ct = predictor.calculate_composite_risk(ht, dt, st_r)
    
    # Show comparison deltas
    st.write("---")
    st.markdown("### 📈 Risk Deltas & Improvements")
    
    dc1, dc2, dc3, dc4 = st.columns(4)
    with dc1:
        draw_delta_card("Composite Risk Index", cb/100.0, ct/100.0)
    with dc2:
        draw_delta_card("Cardiovascular Risk", hb, ht)
    with dc3:
        draw_delta_card("Metabolic Risk", db, dt)
    with dc4:
        draw_delta_card("Cerebrovascular Risk", sb, st_r)

# ==========================================
# PORTAL 3: BATCH PROCESSING PORTAL
# ==========================================
elif portal_view == "📊 Batch Processing Portal":
    st.markdown("## 📊 Batch Prediction & Population Analytics")
    st.write("Process bulk patient datasets via CSV upload. Appends predicted risk columns and provides cohort stats.")
    st.write("---")
    
    col_u1, col_u2 = st.columns([6, 4])
    
    with col_u2:
        st.markdown("#### Sample Template Guide")
        st.write("The uploaded CSV should have the following headers:")
        st.code("age,gender,BMI,systolic_bp,diastolic_bp,cholesterol,glucose,smoking,physical_activity", language="text")
        
        # Download template
        sample_df = pd.DataFrame([{
            "age": 45, "gender": "Male", "BMI": 26.5, "systolic_bp": 120, "diastolic_bp": 80,
            "cholesterol": 195, "glucose": 90, "smoking": "No", "physical_activity": "Yes"
        }])
        sample_csv = sample_df.to_csv(index=False)
        st.download_button("Download CSV Sample Template", sample_csv, "CareGradients_Batch_Template.csv", "text/csv")
        
    with col_u1:
        st.markdown("#### Upload Cohort File")
        uploaded_file = st.file_uploader("Drag & drop patient CSV sheet here", type=["csv"])
        
        if uploaded_file is not None:
            try:
                cohort_df = pd.read_csv(uploaded_file)
                st.success(f"File loaded successfully: {uploaded_file.name} ({len(cohort_df)} records)")
                
                # Check columns
                required_cols = ["age", "gender", "BMI", "systolic_bp", "diastolic_bp", "cholesterol", "glucose", "smoking", "physical_activity"]
                missing_cols = [c for c in required_cols if c not in cohort_df.columns]
                
                if missing_cols:
                    st.error(f"Missing required columns in CSV: {', '.join(missing_cols)}")
                else:
                    # Run predictions
                    with st.spinner("Processing clinical classifiers..."):
                        heart_list, diab_list, stroke_list, composite_list = [], [], [], []
                        
                        for idx, row in cohort_df.iterrows():
                            # Map gender
                            g_val = 1.0 if str(row["gender"]).lower().strip() == "male" else 0.0
                            # Map smoking
                            s_val = 1.0 if str(row["smoking"]).lower().strip() == "yes" else 0.0
                            # Map activity
                            a_val = 1.0 if str(row["physical_activity"]).lower().strip() == "yes" else 0.0
                            
                            BMI_val = float(row["BMI"])
                            cat_str = "underweight" if BMI_val < 18.5 else "normal" if BMI_val < 25.0 else "overweight" if BMI_val < 30.0 else "obese"
                            sys_bp = int(row["systolic_bp"])
                            dia_bp = int(row["diastolic_bp"])
                            
                            prof = {
                                "age": int(row["age"]), "age_decade": int(row["age"] // 10), "gender": g_val,
                                "BMI": BMI_val, "BMI_cat": cat_str, "systolic_bp": sys_bp, "diastolic_bp": dia_bp,
                                "pulse_pressure": sys_bp - dia_bp, "cholesterol": int(row["cholesterol"]), "glucose": int(row["glucose"]),
                                "smoking": s_val, "physical_activity": a_val,
                                "cigs_per_day": 0.0, "bp_meds": 0.0, "prevalent_hypertension": 0.0, "heart_rate": 72.0,
                                "alcohol": 0.0, "heavy_alcohol": 0.0, "prevalent_stroke": 0.0, "heart_disease_history": 0.0,
                                "diabetes_history": 0.0, "height": 170.0, "weight": 70.0, "ap_low": float(dia_bp),
                                # missing flags
                                "age_missing": 0.0, "gender_missing": 0.0, "BMI_missing": 0.0, "BMI_cat_missing": 0.0,
                                "systolic_bp_missing": 0.0, "diastolic_bp_missing": 0.0, "pulse_pressure_missing": 0.0,
                                "cholesterol_missing": 0.0, "glucose_missing": 0.0, "smoking_missing": 0.0,
                                "physical_activity_missing": 0.0, "cigs_per_day_missing": 0.0, "bp_meds_missing": 0.0,
                                "prevalent_hypertension_missing": 0.0, "heart_rate_missing": 0.0, "alcohol_missing": 0.0,
                                "heavy_alcohol_missing": 0.0, "prevalent_stroke_missing": 0.0, "heart_disease_history_missing": 0.0,
                                "diabetes_history_missing": 0.0, "height_missing": 0.0, "weight_missing": 0.0, "ap_low_missing": 0.0
                            }
                            
                            h_r = predictor.predict_risk(prof, "heart")
                            d_r = predictor.predict_risk(prof, "diabetes")
                            s_r = predictor.predict_risk(prof, "stroke")
                            c_r = predictor.calculate_composite_risk(h_r, d_r, s_r)
                            
                            heart_list.append(round(h_r*100, 1))
                            diab_list.append(round(d_r*100, 1))
                            stroke_list.append(round(s_r*100, 1))
                            composite_list.append(c_r)
                            
                        cohort_df["Heart_Risk_Pct"] = heart_list
                        cohort_df["Diabetes_Risk_Pct"] = diab_list
                        cohort_df["Stroke_Risk_Pct"] = stroke_list
                        cohort_df["Composite_Risk_Index"] = composite_list
                        
                        st.subheader("Processed Patient Grid (Preview)")
                        st.dataframe(cohort_df.head(10))
                        
                        # Download results CSV
                        results_csv = cohort_df.to_csv(index=False)
                        st.download_button("📥 Download Annotated Predictions CSV", results_csv, "CareGradients_Cohort_Predictions.csv", "text/csv")
                        
                        # Population summaries
                        st.write("---")
                        st.subheader("📊 Cohort Population Analytics")
                        pc1, pc2, pc3, pc4 = st.columns(4)
                        pc1.metric("Average Heart Risk", f"{np.mean(heart_list):.1f}%")
                        pc2.metric("Average Diabetes Risk", f"{np.mean(diab_list):.1f}%")
                        pc3.metric("Average Stroke Risk", f"{np.mean(stroke_list):.1f}%")
                        pc4.metric("Average Composite Index", f"{np.mean(composite_list):.1f}%")
                        
            except Exception as e:
                st.error(f"Error reading or processing batch CSV file. Details: {e}")

# ==========================================
# PORTAL 4: CLINICAL REGISTRY DATABASE
# ==========================================
elif portal_view == "🗃️ Clinical Registry Database":
    st.markdown("## 🗃️ Clinical Registry Database")
    st.write("Review, filter, and export logged patient risk reports saved from the Diagnostic Suite.")
    st.write("---")
    
    # Search query
    search = st.text_input("🔍 Search patient records by Name or Patient ID")
    records_df = load_records(search_query=search)
    
    if records_df.empty:
        st.info("No logs matched search filters or database is currently empty.")
    else:
        st.markdown(f"Total Registered Records: **{len(records_df)}**")
        st.dataframe(records_df, use_container_width=True)
        
        # Action columns: Export & Delete
        ac1, ac2 = st.columns([6, 4])
        
        with ac1:
            db_csv = records_df.to_csv(index=False)
            st.download_button("📥 Export Registry to CSV", db_csv, "CareGradients_Clinical_Registry.csv", "text/csv")
            
        with ac2:
            st.markdown("#### Remove Record")
            with st.form("delete_form", clear_on_submit=True):
                del_id = st.selectbox("Select ID to delete", records_df["id"].values)
                del_submit = st.form_submit_button("Delete Log Permanently")
                
                if del_submit:
                    delete_record(del_id)
                    st.success(f"Record #{del_id} successfully deleted.")
                    st.experimental_rerun()

# ==========================================
# PORTAL 5: CLINICAL GUIDELINES
# ==========================================
elif portal_view == "📘 Targets & Guidelines":
    st.markdown("## 📘 Clinical Targets & Reference Guidelines")
    st.write("Reference standards for cardiovascular, metabolic, and cerebrovascular healthcare indicators.")
    st.write("---")
    
    col_ref1, col_ref2 = st.columns(2)
    
    with col_ref1:
        st.markdown(
            """
            ### ❤️ Hypertension & Blood Pressure Guidelines
            * **Ideal target**: Below `120/80 mmHg`.
            * **Elevated**: Systolic between `120-129` and diastolic below `80`.
            * **Stage 1 Hypertension**: Systolic `130-139` or diastolic `80-89`.
            * **Stage 2 Hypertension**: Systolic `140+` or diastolic `90+`.
            * **Clinical Action**: Stage 1 warrants lifestyle changes and possible therapy. Stage 2 requires immediate medical consult.
            
            ### 🍭 Diabetes Screening Thresholds
            * **Normal fasting glucose**: `70 - 99 mg/dL`.
            * **Prediabetes**: `100 - 125 mg/dL`.
            * **Diabetes**: `126 mg/dL` or higher on two separate tests.
            * **HbA1c Target**: Below `5.7%` is normal. `5.7% - 6.4%` is prediabetes. `6.5%+` is diabetic.
            """
        )
        
    with col_ref2:
        st.markdown(
            """
            ### 📉 Dyslipidemia & Lipids Metrics
            * **Total Cholesterol target**: Below `200 mg/dL`.
            * **Borderline high**: `200 - 239 mg/dL`.
            * **High risk levels**: `240 mg/dL` or higher.
            * **LDL Targets**: Ideally below `100 mg/dL` (lower for patients with cardiac history).
            * **HDL Targets**: Above `40 mg/dL` (men) or `50 mg/dL` (women) is cardioprotective.
            
            ### ⚖️ BMI Classification Values
            * **Underweight**: Below `18.5`.
            * **Healthy Weight**: `18.5 - 24.9`.
            * **Overweight**: `25.0 - 29.9`.
            * **Obese**: `30.0` or higher.
            """
        )
