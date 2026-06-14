from datetime import datetime

def generate_html_report(patient_id, patient_name, profile: dict, heart_p: float, diabetes_p: float, stroke_p: float, composite_p: float) -> str:
    """
    Compiles patient diagnostic inputs and predicted risk metrics into a styled,
    printable HTML document.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Calculate risk category classes
    def get_risk_badge(prob):
        pct = prob * 100
        if pct < 15.0:
            return '<span class="badge badge-low">Low Risk</span>'
        elif pct < 35.0:
            return '<span class="badge badge-moderate">Moderate Risk</span>'
        else:
            return '<span class="badge badge-high">High Risk</span>'

    # Build recommendations list based on clinical thresholds
    recommendations = []
    if profile.get("systolic_bp", 120) >= 130 or profile.get("diastolic_bp", 80) >= 80:
        recommendations.append("<strong>Blood Pressure Alert:</strong> Readings indicate elevated levels. Schedule cardiovascular monitoring and restrict dietary sodium.")
    if profile.get("glucose", 95) >= 100:
        recommendations.append("<strong>Glycemic Alert:</strong> Fasting blood glucose is elevated. Monitor glycemic index intake and check HbA1c levels.")
    if profile.get("cholesterol", 190) >= 200:
        recommendations.append("<strong>Lipid Profile Alert:</strong> Total cholesterol exceeds recommended limits. Reduce saturated fats and check HDL/LDL splits.")
    if profile.get("BMI", 25.0) >= 25.0:
        recommendations.append("<strong>Body Mass Indicator:</strong> Weight index falls outside ideal limits. Incorporate regular physical activity and caloric adjustments.")
    if profile.get("smoking", 0.0) == 1.0:
        recommendations.append("<strong>Smoking Cessation:</strong> Highly advised. Current smoking habits multiply cardiovascular risks and compromise endothelial health.")
    if profile.get("physical_activity", 1.0) == 0.0:
        recommendations.append("<strong>Sedentary Lifestyle:</strong> Incorporate at least 150 minutes of aerobic exercise weekly to improve insulin response.")
        
    if not recommendations:
        recommendations.append("Keep maintaining your healthy lifestyle. All primary metrics are currently within recommended clinical limits.")

    recommendation_items_html = "".join([f"<li>{rec}</li>" for rec in recommendations])

    # Printable light-themed high-contrast report design
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>CareGradients AI - Clinical Report</title>
        <style>
            body {{
                font-family: 'Helvetica Neue', Arial, sans-serif;
                background-color: #ffffff;
                color: #2d3748;
                line-height: 1.6;
                padding: 40px;
                margin: 0;
            }}
            .header {{
                border-bottom: 2px solid #2b6cb0;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                font-size: 26px;
                color: #2b6cb0;
                margin: 0;
                font-weight: 700;
            }}
            .header p {{
                margin: 5px 0 0 0;
                color: #718096;
                font-size: 14px;
            }}
            .section-title {{
                font-size: 18px;
                color: #2b6cb0;
                border-bottom: 1px solid #e2e8f0;
                padding-bottom: 6px;
                margin-top: 30px;
                margin-bottom: 15px;
                font-weight: 600;
            }}
            .meta-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
                background-color: #f7fafc;
                padding: 15px 20px;
                border-radius: 6px;
                border: 1px solid #e2e8f0;
                margin-bottom: 25px;
            }}
            .meta-item span {{
                font-weight: bold;
                color: #4a5568;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 25px;
            }}
            th, td {{
                border: 1px solid #e2e8f0;
                padding: 10px 12px;
                text-align: left;
            }}
            th {{
                background-color: #ebf8ff;
                color: #2b6cb0;
                font-weight: 600;
            }}
            .results-grid {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                margin-bottom: 25px;
            }}
            .result-card {{
                border: 1px solid #cbd5e0;
                border-radius: 6px;
                padding: 15px;
                text-align: center;
                background-color: #fff;
            }}
            .result-card.composite {{
                border: 2px solid #2b6cb0;
                background-color: #ebf8ff;
            }}
            .card-title {{
                font-size: 12px;
                text-transform: uppercase;
                color: #718096;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .card-value {{
                font-size: 24px;
                font-weight: bold;
                color: #2d3748;
                margin: 5px 0;
            }}
            .composite .card-value {{
                color: #2b6cb0;
                font-size: 28px;
            }}
            .badge {{
                display: inline-block;
                padding: 3px 8px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: bold;
                text-transform: uppercase;
            }}
            .badge-low {{ background-color: #c6f6d5; color: #22543d; }}
            .badge-moderate {{ background-color: #feebc8; color: #744210; }}
            .badge-high {{ background-color: #fed7d7; color: #742a2a; }}
            
            ul {{
                padding-left: 20px;
                margin: 0;
            }}
            li {{
                margin-bottom: 8px;
            }}
            .footer {{
                margin-top: 50px;
                border-top: 1px solid #e2e8f0;
                padding-top: 15px;
                text-align: center;
                font-size: 12px;
                color: #a0aec0;
            }}
            @media print {{
                body {{ padding: 20px; }}
                .no-print {{ display: none; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>CareGradients AI - Clinical Assessment Summary</h1>
            <p>Generated automatically on {timestamp} | System Release v2.0</p>
        </div>

        <div class="section-title">Patient Profile Information</div>
        <div class="meta-grid">
            <div class="meta-item"><span>Patient ID:</span> {patient_id}</div>
            <div class="meta-item"><span>Patient Name:</span> {patient_name}</div>
            <div class="meta-item"><span>Age / Gender:</span> {profile.get("age", "N/A")} years / {"Male" if profile.get("gender", 0) == 1.0 else "Female"}</div>
            <div class="meta-item"><span>Calculated BMI:</span> {profile.get("BMI", "N/A")} ({profile.get("BMI_cat", "N/A").upper()})</div>
        </div>

        <div class="section-title">Diagnostic Risk Scoring</div>
        <div class="results-grid">
            <div class="result-card composite">
                <div class="card-title">Composite Index</div>
                <div class="card-value">{composite_p}%</div>
                <span class="badge" style="background-color: #bee3f8; color: #2a4365;">Combined</span>
            </div>
            <div class="result-card">
                <div class="card-title">Heart Disease</div>
                <div class="card-value">{(heart_p*100):.1f}%</div>
                {get_risk_badge(heart_p)}
            </div>
            <div class="result-card">
                <div class="card-title">Diabetes Risk</div>
                <div class="card-value">{(diabetes_p*100):.1f}%</div>
                {get_risk_badge(diabetes_p)}
            </div>
            <div class="result-card">
                <div class="card-title">Stroke Probability</div>
                <div class="card-value">{(stroke_p*100):.1f}%</div>
                {get_risk_badge(stroke_p)}
            </div>
        </div>

        <div class="section-title">Clinical Vitals and Habits Summary</div>
        <table>
            <thead>
                <tr>
                    <th>Clinical Parameter</th>
                    <th>Measured Value</th>
                    <th>Clinical Target / Baseline Range</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Systolic / Diastolic Blood Pressure</td>
                    <td>{profile.get("systolic_bp", 120)} / {profile.get("diastolic_bp", 80)} mmHg</td>
                    <td>Ideal: &lt; 120/80 mmHg</td>
                </tr>
                <tr>
                    <td>Total Cholesterol</td>
                    <td>{profile.get("cholesterol", 190)} mg/dL</td>
                    <td>Normal: &lt; 200 mg/dL</td>
                </tr>
                <tr>
                    <td>Fasting Blood Glucose</td>
                    <td>{profile.get("glucose", 95)} mg/dL</td>
                    <td>Normal: &lt; 100 mg/dL</td>
                </tr>
                <tr>
                    <td>Active Smoking</td>
                    <td>{"Yes" if profile.get("smoking", 0.0) == 1.0 else "No"}</td>
                    <td>Target: Non-smoker</td>
                </tr>
                <tr>
                    <td>Physically Active</td>
                    <td>{"Yes" if profile.get("physical_activity", 1.0) == 1.0 else "No"}</td>
                    <td>Target: Yes (150+ mins weekly)</td>
                </tr>
            </tbody>
        </table>

        <div class="section-title">Targeted Recommendations & Intervention Goals</div>
        <ul>
            {recommendation_items_html}
        </ul>

        <div class="footer">
            <p>Confidential Medical Document. CareGradients AI classifier output for screening support only.</p>
        </div>
    </body>
    </html>
    """
    return html_content
