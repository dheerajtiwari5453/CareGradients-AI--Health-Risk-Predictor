import streamlit as st

def apply_custom_styles():
    """
    Injects custom CSS overrides into the Streamlit app to deliver a premium
    dark mode clinical dashboard aesthetic.
    """
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        
        /* Set base font */
        html, body, [class*="css"], .stApp {
            font-family: 'Outfit', sans-serif;
        }
        
        /* App layout styling */
        .stApp {
            background-color: #0b0f19;
            color: #e2e8f0;
        }
        
        /* Sidebar layout styling */
        [data-testid="stSidebar"] {
            background-color: #0f1626;
            border-right: 1px solid #1e293b;
        }
        
        /* Streamlit widget tweaks */
        .stSlider [data-testid="stWidgetLabel"] {
            font-weight: 500;
            color: #cbd5e1;
        }
        .stSelectbox [data-testid="stWidgetLabel"] {
            font-weight: 500;
            color: #cbd5e1;
        }
        
        /* Clinical Card containers */
        .risk-card {
            background: linear-gradient(145deg, #131c31 0%, #0f172a 100%);
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            margin-bottom: 15px;
        }
        
        .risk-card:hover {
            transform: translateY(-3px);
            border-color: #3b82f6;
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
        }
        
        .risk-title {
            font-size: 13px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            font-weight: 600;
            margin-bottom: 6px;
        }
        
        .risk-value {
            font-size: 32px;
            font-weight: 700;
            margin: 8px 0;
            color: #ffffff;
        }
        
        /* Score colorations based on risk levels */
        .color-heart {
            background: -webkit-linear-gradient(45deg, #ff4d4d, #ff8080);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .color-diabetes {
            background: -webkit-linear-gradient(45deg, #ff9f43, #ffc048);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .color-stroke {
            background: -webkit-linear-gradient(45deg, #9b59b6, #c56cf0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Custom styled badges */
        .badge {
            display: inline-block;
            padding: 3px 9px;
            border-radius: 30px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .badge-low {
            background-color: rgba(46, 196, 182, 0.12);
            color: #2ec4b6;
            border: 1px solid rgba(46, 196, 182, 0.25);
        }
        
        .badge-moderate {
            background-color: rgba(255, 159, 67, 0.12);
            color: #ff9f43;
            border: 1px solid rgba(255, 159, 67, 0.25);
        }
        
        .badge-high {
            background-color: rgba(238, 82, 83, 0.12);
            color: #ee5253;
            border: 1px solid rgba(238, 82, 83, 0.25);
        }
        
        /* Delta indicator classes */
        .delta-negative {
            background-color: rgba(46, 196, 182, 0.15);
            color: #2ec4b6;
            border: 1px solid rgba(46, 196, 182, 0.3);
        }
        .delta-positive {
            background-color: rgba(238, 82, 83, 0.15);
            color: #ee5253;
            border: 1px solid rgba(238, 82, 83, 0.3);
        }
        .delta-neutral {
            background-color: rgba(100, 116, 139, 0.15);
            color: #94a3b8;
            border: 1px solid rgba(100, 116, 139, 0.3);
        }
        
        /* Composite Risk Dial Panel */
        .composite-panel {
            background: radial-gradient(circle at 10% 20%, #1e293b 0%, #0f172a 100%);
            border: 1.5px solid #2563eb;
            border-radius: 14px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 0 20px rgba(37, 99, 235, 0.15);
            margin: 15px 0 25px 0;
        }
        
        .composite-title {
            font-size: 15px;
            font-weight: 600;
            color: #94a3b8;
            letter-spacing: 1px;
        }
        
        .composite-val {
            font-size: 48px;
            font-weight: 800;
            color: #3b82f6;
            text-shadow: 0 0 8px rgba(59, 130, 246, 0.4);
            margin: 10px 0;
        }
        
        /* Clinical Disclaimer */
        .disclaimer-box {
            background-color: rgba(245, 158, 11, 0.04);
            color: #f59e0b;
            border-left: 3px solid #f59e0b;
            padding: 10px 18px;
            border-radius: 4px;
            font-size: 12.5px;
            margin: 20px 0;
            line-height: 1.5;
        }
        
        /* Tab formatting overrides */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 42px;
            background-color: #1e293b;
            border-radius: 6px 6px 0 0;
            border: 1px solid #334155;
            border-bottom: none;
            color: #94a3b8;
            padding: 8px 18px;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background-color: #2563eb !important;
            color: #ffffff !important;
            border-color: #2563eb !important;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
def draw_card(title: str, probability: float, color_class: str):
    """
    Renders a clinical risk card with HTML formatting.
    """
    pct = probability * 100
    if pct < 15.0:
        badge_html = '<span class="badge badge-low">Low Risk</span>'
    elif pct < 35.0:
        badge_html = '<span class="badge badge-moderate">Moderate Risk</span>'
    else:
        badge_html = '<span class="badge badge-high">High Risk</span>'
        
    st.markdown(
        f"""
        <div class="risk-card">
            <div class="risk-title">{title}</div>
            <div class="risk-value {color_class}">{pct:.1f}%</div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True
    )

def draw_delta_card(title: str, base_prob: float, compare_prob: float):
    """
    Renders a side-by-side risk comparison card with delta change indication.
    """
    base_pct = base_prob * 100
    comp_pct = compare_prob * 100
    diff = comp_pct - base_pct
    
    if diff < -0.05:
        diff_class = "delta-negative"
        diff_text = f"↓ {abs(diff):.1f}% reduction"
    elif diff > 0.05:
        diff_class = "delta-positive"
        diff_text = f"↑ {abs(diff):.1f}% increase"
    else:
        diff_class = "delta-neutral"
        diff_text = "No change"
        
    st.markdown(
        f"""
        <div class="risk-card">
            <div class="risk-title">{title}</div>
            <div style="display: flex; justify-content: space-around; align-items: center; margin: 10px 0;">
                <div>
                    <div style="font-size: 10px; color: #94a3b8; font-weight:600;">BASELINE</div>
                    <div style="font-size: 20px; font-weight: 700; color: #ffffff;">{base_pct:.1f}%</div>
                </div>
                <div style="font-size: 18px; color: #475569;">➔</div>
                <div>
                    <div style="font-size: 10px; color: #94a3b8; font-weight:600;">COMPARE</div>
                    <div style="font-size: 20px; font-weight: 700; color: #ffffff;">{comp_pct:.1f}%</div>
                </div>
            </div>
            <div class="badge {diff_class}">{diff_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
