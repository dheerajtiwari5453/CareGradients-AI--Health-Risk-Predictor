import matplotlib.pyplot as plt
import numpy as np

def run_sensitivity_analysis(predictor, patient_profile: dict, disease_key: str) -> list:
    """
    Calculates the impact of perturbing individual clinical/lifestyle metrics
    on the predicted risk score. Adjusts correlated engineered features in real-time.
    """
    baseline_risk = predictor.predict_risk(patient_profile, disease_key)
    
    # Establish local perturbation variations
    perturbations = {
        "age": patient_profile.get("age", 23) + 5,
        "BMI": patient_profile.get("BMI", 28.0) + 2.0,
        "systolic_bp": patient_profile.get("systolic_bp", 120) + 10,
        "diastolic_bp": patient_profile.get("diastolic_bp", 80) + 5,
        "cholesterol": patient_profile.get("cholesterol", 200) + 20,
        "glucose": patient_profile.get("glucose", 100) + 20,
        "smoking": 1.0 - float(patient_profile.get("smoking", 0.0)),
        "physical_activity": 1.0 - float(patient_profile.get("physical_activity", 0.0))
    }
    
    # Add optional advanced fields if they exist in user profile
    optional_keys = ["bp_meds", "cigs_per_day", "alcohol", "prevalent_hypertension", "heart_disease_history", "prevalent_stroke", "diabetes_history"]
    for key in optional_keys:
        if key in patient_profile:
            if key == "cigs_per_day" and patient_profile["smoking"] == 1.0:
                perturbations["cigs_per_day"] = patient_profile[key] + 5
            elif key in ["bp_meds", "alcohol", "prevalent_hypertension", "heart_disease_history", "prevalent_stroke", "diabetes_history"]:
                perturbations[key] = 1.0 - float(patient_profile[key])
                
    sensitivity_records = []
    
    for feature, perturbed_val in perturbations.items():
        scenario_profile = patient_profile.copy()
        scenario_profile[feature] = perturbed_val
        
        # Synchronize dependent engineered variables
        if feature == "BMI":
            bmi = perturbed_val
            scenario_profile["BMI_cat"] = (
                "underweight" if bmi < 18.5 else
                "normal" if bmi < 25.0 else
                "overweight" if bmi < 30.0 else
                "obese"
            )
            # Update weight if height is present
            if "height" in scenario_profile and scenario_profile["height"] > 0:
                h_m = scenario_profile["height"] / 100.0
                scenario_profile["weight"] = round(bmi * (h_m ** 2), 1)
                
        elif feature == "age":
            scenario_profile["age_decade"] = int(perturbed_val // 10)
            
        elif feature in ["systolic_bp", "diastolic_bp"]:
            scenario_profile["pulse_pressure"] = scenario_profile["systolic_bp"] - scenario_profile["diastolic_bp"]
            
        perturbed_risk = predictor.predict_risk(scenario_profile, disease_key)
        risk_shift = perturbed_risk - baseline_risk
        sensitivity_records.append((feature, risk_shift))
        
    # Order by magnitude of influence
    sensitivity_records.sort(key=lambda entry: abs(entry[1]), reverse=True)
    return sensitivity_records

def generate_sensitivity_plot(sensitivity_records: list, disease_title: str):
    """
    Renders a premium, transparent horizontal bar chart mapping risk factor sensitivities.
    """
    # Isolate top 6 drivers
    top_records = sensitivity_records[:6]
    labels = [item[0].replace("_", " ").title() for item in top_records]
    percentages = [item[1] * 100 for item in top_records]
    
    # Invert order for correct vertical bar plotting orientation
    labels.reverse()
    percentages.reverse()
    
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor='none')
    ax.set_facecolor('none')
    
    # Palette definition: Coral Red (+ risk), Soft Teal (- risk)
    bar_colors = ['#FF6F61' if pct >= 0 else '#2EC4B6' for pct in percentages]
    
    bars = ax.barh(labels, percentages, color=bar_colors, height=0.6, alpha=0.9, edgecolor='none')
    
    # Hide top/right borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#4A5568')
    ax.spines['bottom'].set_color('#4A5568')
    
    ax.tick_params(colors='#E2E8F0', labelsize=10)
    ax.grid(axis='x', linestyle=':', alpha=0.25, color='#CBD5E0')
    
    # Zero baseline line
    ax.axvline(0, color='#718096', linewidth=1.0, linestyle='-')
    
    ax.set_xlabel("Risk Shift (Percentage Points)", color='#E2E8F0', fontsize=10, labelpad=8)
    ax.set_title(f"Clinical Risk Driver Sensitivity ({disease_title.title()})", color='#FFFFFF', fontsize=12, pad=15, fontweight='bold')
    
    # Annotate bars
    for bar in bars:
        width = bar.get_width()
        alignment = 'left' if width >= 0 else 'right'
        padding = 0.25 if width >= 0 else -0.25
        text_color = '#FF8A7F' if width >= 0 else '#4FE3D4'
        
        ax.text(
            width + padding, 
            bar.get_y() + bar.get_height() / 2, 
            f"{width:+.1f}%", 
            va='center', 
            ha=alignment, 
            color=text_color, 
            fontweight='bold', 
            fontsize=9
        )
        
    plt.tight_layout()
    return fig
