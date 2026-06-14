import matplotlib.pyplot as plt
import numpy as np

def generate_radar_chart(patient_profile: dict, heart_p: float, diabetes_p: float, stroke_p: float):
    """
    Draws an interactive 5-axis clinical radar (spider) plot comparing
    patient metrics against reference healthy baselines.
    """
    categories = [
        'Cardiovascular Risk', 
        'Metabolic Risk', 
        'Cerebrovascular Risk', 
        'Blood Pressure Index', 
        'Body Mass Index'
    ]
    
    # BP Index: Normal = 120. Map range 90-200 to 0-100%
    sys_bp = patient_profile.get("systolic_bp", 120)
    bp_pct = np.clip((sys_bp - 90) / 110.0 * 100.0, 10.0, 100.0)
    
    # BMI Index: Normal = 24. Map range 15-45 to 0-100%
    bmi_val = patient_profile.get("BMI", 25.0)
    bmi_pct = np.clip((bmi_val - 15) / 30.0 * 100.0, 10.0, 100.0)
    
    values = [
        heart_p * 100.0,
        diabetes_p * 100.0,
        stroke_p * 100.0,
        bp_pct,
        bmi_pct
    ]
    
    # Ideal clinical limits for baseline
    healthy_baseline = [15.0, 15.0, 15.0, 27.2, 30.0] # 15% risk ceilings, healthy BP & BMI thresholds
    
    num_vars = len(categories)
    
    # Determine axes coordinates
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    
    # Close the geometry loop
    values += values[:1]
    healthy_baseline += healthy_baseline[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(5.5, 4.5), subplot_kw=dict(polar=True), facecolor='none')
    ax.set_facecolor('none')
    
    # Draw radial lines and set parameters
    plt.xticks(angles[:-1], categories, color='#CBD5E1', size=9, fontweight='bold')
    
    # Configure grid lines
    ax.set_rlabel_position(30)
    plt.yticks([25, 50, 75, 100], ["25%", "50%", "75%", "100%"], color="#64748B", size=8)
    plt.ylim(0, 100)
    
    # Customise grid gridlines
    ax.grid(color='#334155', linestyle=':', alpha=0.6)
    
    # Plot benchmark limits (healthy zone)
    ax.plot(angles, healthy_baseline, color='#0ea5e9', linewidth=1.5, linestyle='--', label='Healthy Benchmark')
    ax.fill(angles, healthy_baseline, color='#0ea5e9', alpha=0.08)
    
    # Plot patient records
    ax.plot(angles, values, color='#ef4444', linewidth=2.0, linestyle='-', label='Patient Profile')
    ax.fill(angles, values, color='#ef4444', alpha=0.22)
    
    # Spine borders color
    ax.spines['polar'].set_color('#1e293b')
    
    # Position legend
    ax.legend(
        loc='upper right', 
        bbox_to_anchor=(1.35, 1.15), 
        facecolor='#0f172a', 
        edgecolor='#1e293b', 
        labelcolor='#e2e8f0',
        fontsize=8.5
    )
    
    plt.tight_layout()
    return fig
