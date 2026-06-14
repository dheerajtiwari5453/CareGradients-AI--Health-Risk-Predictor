# CareGradients AI: Explainable Risk Intelligence & Patient Registry

CareGradients AI is a modular, clinical-grade machine learning application designed to assess, visualize, and log cumulative health risks across three primary categories: **Cardiovascular Disease**, **Metabolic Disorders (Diabetes)**, and **Cerebrovascular Disease (Stroke)**.

Built on optimized XGBoost classifiers and wrapped in a custom, glassmorphic Streamlit dashboard, this application provides clinical practitioners and health educators with real-time risk scores, interactive local sensitivity explanations, relatioinal database records logging, batch predictions, and comparative delta diagnostics.

---

## 🚀 Key Features

1. **Interactive Diagnostic Suite**:
   - **Demographics & Vitals**: Slide controls for patient attributes (Age, BMI, Blood Pressure, Cholesterol, Glucose, Smoking, Activity).
   - **Advanced Clinical Indicators**: Expandable controls for detailed diagnostics supported by the models (e.g., Blood Pressure Medication, history of hypertension, resting heart rate, height/weight metrics).
   - **Medical Radar Diagnostics**: Renders a 5-axis clinical radar map plotting the patient's parameters against ideal healthy baselines.
   - **Interactive Model Interpretability**: Exposes local sensitivity gradients using styled horizontal bar charts (Matplotlib), allowing users to select and analyze the primary risk drivers.
   - **Clinical Document Generator**: Generates and downloads print-friendly HTML clinical reports.
2. **Intervention Delta Analyzer (Comparative Analysis)**:
   - Model the relative impact of clinical changes (e.g., smoking cessation, pressure control) by comparing baseline profiles against intervention targets side-by-side with risk reduction deltas.
3. **Batch Prediction Engine (CSV Upload)**:
   - Processes bulk patient datasets via CSV drag-and-drop. Appends predicted risk columns, provides cohort summaries (averages), and exports predictions as a downloadable CSV.
4. **Clinical Registry Database (SQLite)**:
    - Save assessments directly to a local SQLite database (`caregradients_records.db`).
    - Query histories, filter by name/ID, delete records, or export the registry database to a consolidated CSV sheet.

---

## 🛠️ Architecture and Project Layout

The codebase is structured as a modular Python package:

```text
├── models/                     # Pre-trained ML artifacts
│   ├── heart_disease_xgb.joblib
│   ├── heart_encoder.joblib
│   └── ...                     # Encoders & feature mappings for stroke and diabetes
├── src/                        # Core codebase package
│   ├── __init__.py
│   ├── predictor.py            # Model registry, preprocessing and category encoder alignments
│   ├── explainers.py           # Sensitivity analysis engine and Matplotlib chart generator
│   ├── visualizations.py       # Matplotlib Radar chart generator
│   ├── database.py             # SQLite CRUD functions for database registry
│   ├── reports.py              # Clinical HTML print report templates
│   └── styles.py               # Custom dark-theme styling sheet and card drawer
├── app.py                      # Main entrypoint script for Streamlit
├── requirements.txt            # Python dependencies
└── readme.md                   # Project documentation
```

---

## 🔬 Machine Learning Pipeline

### Model Base Classifiers
The predictive engine utilizes **XGBoost Classifiers** trained on clinical repositories including the **Framingham Heart Study** (for cardiovascular models) and **CDC Diabetes Health Indicators** (for metabolic models).

### Sensitivity-Based Interpretability
The sensitivity graphs model local gradients by testing marginal alterations. A positive shift indicates that increasing or activating the feature raises the patient's risk profile. The engine synchronizes correlated parameters (such as recalculating BMI categories and pulse pressures) during perturbations.

---

## 📦 Getting Started

### 1. Install Dependencies
Install all required packages listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
Run the Streamlit server from the root directory:
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser to view the CareGradients AI dashboard.