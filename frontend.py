import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Premium Guard | Lifestyle & Insurance Premium Predictor",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- THEME TOGGLE PATTERN ---
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

IS_DARK = st.session_state.theme == "dark"

# --- COLOR PALETTE AND DESIGN SYSTEM CSS ---
BG_COLOR = "#09090b" if IS_DARK else "#ffffff"
BG_SUBTLE = "#0c0c0f" if IS_DARK else "#f9fafb"
CARD_COLOR = "#0c0c0f" if IS_DARK else "#ffffff"
CARD_HOVER = "#131316" if IS_DARK else "#f4f4f5"
BORDER_COLOR = "#1e1e24" if IS_DARK else "#e4e4e7"
BORDER_SUBTLE = "#16161a" if IS_DARK else "#f0f0f2"
TEXT_COLOR = "#fafafa" if IS_DARK else "#09090b"
TEXT_MUTED = "#71717a"
TEXT_DIM = "#52525b" if IS_DARK else "#a1a1aa"
ACCENT_COLOR = "#2563eb"
GREEN_COLOR = "#22c55e" if IS_DARK else "#16a34a"
GREEN_MUTED = "rgba(34,197,94,0.12)" if IS_DARK else "rgba(22,163,74,0.08)"
RED_COLOR = "#ef4444" if IS_DARK else "#dc2626"
RED_MUTED = "rgba(239,68,68,0.12)" if IS_DARK else "rgba(220,38,38,0.08)"
AMBER_COLOR = "#f59e0b" if IS_DARK else "#d97706"
AMBER_MUTED = "rgba(245,158,11,0.12)" if IS_DARK else "rgba(217,119,6,0.08)"
SHADOW = "none" if IS_DARK else "0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03)"

custom_css = f"""
<style>
    /* Hide Streamlit chrome */
    header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stDeployButton"],
    [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"],
    div[data-testid="stSidebarCollapsedControl"] {{
        display: none !important;
    }}
    
    /* Global Styling */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {{
        background-color: {BG_COLOR} !important;
        color: {TEXT_COLOR} !important;
        font-family: 'DM Sans', -apple-system, sans-serif !important;
    }}
    .block-container {{
        padding: 2rem 2.5rem 3rem !important;
        max-width: 1360px !important;
    }}
    
    /* Column Gap layout */
    [data-testid="stHorizontalBlock"] {{
        gap: 1.5rem !important;
    }}
    [data-testid="stVerticalBlock"] > div:has(> [data-testid="stHorizontalBlock"]) {{
        margin-bottom: 0.5rem !important;
    }}

    /* Card styling */
    .premium-card {{
        background: {CARD_COLOR};
        border: 1px solid {BORDER_COLOR};
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: {SHADOW};
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    .premium-card:hover {{
        border-color: {ACCENT_COLOR};
    }}
    
    /* Brand Header styling */
    .brand {{
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1.5rem;
    }}
    .brand-emoji {{
        font-size: 2rem;
        color: {ACCENT_COLOR};
        line-height: 1;
    }}
    .brand-name {{
        font-size: 1.75rem;
        font-weight: 800;
        color: {TEXT_COLOR};
        letter-spacing: -0.03em;
    }}
    .brand-tag {{
        font-size: 0.8rem;
        color: {TEXT_MUTED};
        background: {BG_SUBTLE};
        border: 1px solid {BORDER_COLOR};
        padding: 3px 10px;
        border-radius: 6px;
        margin-left: 10px;
        font-weight: 500;
    }}

    /* Metric Card styling */
    .metric-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1-fraction));
        gap: 1rem;
        margin-bottom: 1rem;
    }}
    .metric-card {{
        background: {CARD_COLOR};
        border: 1px solid {BORDER_COLOR};
        border-radius: 10px;
        padding: 1rem 1.25rem;
        box-shadow: {SHADOW};
        text-align: left;
    }}
    .metric-label {{
        font-size: 0.75rem;
        color: {TEXT_MUTED};
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }}
    .metric-value {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {TEXT_COLOR};
        letter-spacing: -0.02em;
    }}
    .metric-badge {{
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 5px;
        margin-top: 0.4rem;
    }}
    .badge-success {{ color: {GREEN_COLOR}; background: {GREEN_MUTED}; }}
    .badge-error {{ color: {RED_COLOR}; background: {RED_MUTED}; }}
    .badge-warning {{ color: {AMBER_COLOR}; background: {AMBER_MUTED}; }}
    .badge-info {{ color: {ACCENT_COLOR}; background: rgba(37,99,235,0.1); }}

    /* Prediction Result styling */
    .predict-box {{
        background: {BG_SUBTLE};
        border: 1px solid {BORDER_COLOR};
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 1.5rem;
    }}
    .predict-title {{
        font-size: 0.85rem;
        color: {TEXT_MUTED};
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
    }}
    .predict-result {{
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin: 0.5rem 0;
    }}
    .result-low {{ color: {GREEN_COLOR}; }}
    .result-medium {{ color: {AMBER_COLOR}; }}
    .result-high {{ color: {RED_COLOR}; }}

    /* Chart wrap styling */
    .chart-wrap {{
        background: {CARD_COLOR};
        border: 1px solid {BORDER_COLOR};
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: {SHADOW};
        margin-bottom: 1.5rem;
    }}
    .chart-title {{
        font-size: 0.875rem;
        font-weight: 700;
        color: {TEXT_COLOR};
    }}
    .chart-subtitle {{
        font-size: 0.75rem;
        color: {TEXT_MUTED};
        margin-bottom: 1rem;
    }}

    /* Custom Streamlit Form inputs custom coloring to match system */
    div.stButton > button {{
        background-color: {ACCENT_COLOR} !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        transition: background-color 0.2s ease !important;
    }}
    div.stButton > button:hover {{
        background-color: #1d4ed8 !important;
    }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- CACHED DATA LOAD ---
@st.cache_data
def get_historical_data():
    try:
        df = pd.read_csv("insurance.csv")
        df["bmi"] = df["weight"] / (df["height"] ** 2)
        return df
    except Exception:
        # Fallback if file missing
        return pd.DataFrame({
            "age": [30, 45, 60, 25],
            "weight": [70.0, 85.0, 95.0, 60.0],
            "height": [1.75, 1.80, 1.65, 1.70],
            "income_lpa": [12.0, 25.0, 5.0, 45.0],
            "bmi": [22.8, 26.2, 34.8, 20.7],
            "insurance_premium_category": ["Low", "Medium", "High", "Low"]
        })

df_history = get_historical_data()

# --- PREDEFINED CITIES (FROM APP.PY TIER CODES) ---
tier_1_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"]
tier_2_cities = [
    "Jaipur", "Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi", "Visakhapatnam", "Coimbatore",
    "Bhopal", "Nagpur", "Vadodara", "Surat", "Rajkot", "Jodhpur", "Raipur", "Amritsar", "Varanasi",
    "Agra", "Dehradun", "Mysore", "Jabalpur", "Guwahati", "Thiruvananthapuram", "Ludhiana", "Nashik",
    "Allahabad", "Udaipur", "Aurangabad", "Hubli", "Belgaum", "Salem", "Vijayawada", "Tiruchirappalli",
    "Bhavnagar", "Gwalior", "Dhanbad", "Bareilly", "Aligarh", "Gaya", "Kozhikode", "Warangal",
    "Kolhapur", "Bilaspur", "Jalandhar", "Noida", "Guntur", "Asansol", "Siliguri", "Kota"
]

all_suggested_cities = sorted(tier_1_cities + tier_2_cities) + ["Other"]

# --- MAP DISPLAY NAMES TO LITERAL OCCUPATION STRINGS ---
occupation_map = {
    "Private Job": "private_job",
    "Government Job": "government_job",
    "Business Owner": "business_owner",
    "Freelancer": "freelancer",
    "Student": "student",
    "Retired": "retired",
    "Unemployed": "unemployed",
    "Engineer": "Engineer",
    "Doctor": "Doctor",
    "Lawyer": "Lawyer",
    "Teacher": "Teacher",
    "Pilot": "Pilot",
    "Architect": "Architect",
    "Banker": "Banker",
    "Developer": "Developer",
    "Chef": "Chef",
    "Writer": "Writer",
    "Artist": "Artist",
    "Musician": "Musician",
    "Actor": "Actor",
    "Dancer": "Dancer",
    "Photographer": "Photographer",
    "Designer": "Designer",
    "Marketing": "Marketing",
    "Sales": "Sales",
    "HR": "HR",
    "Finance": "Finance",
    "Consultant": "Consultant",
    "Entrepreneur": "Entrepreneur",
    "Other": "Other"
}

# --- HEADER WITH BRAND AND THEME TOGGLE ---
head_left, head_right = st.columns([8, 1])
with head_left:
    st.markdown("""
    <div class="brand">
        <span class="brand-emoji">◆</span>
        <span class="brand-name">Premium Guard</span>
        <span class="brand-tag">AI Lifestyle & Insurance Risk Engine</span>
    </div>
    """, unsafe_allow_html=True)
with head_right:
    theme_label = "☀️ Light" if IS_DARK else "🌙 Dark"
    st.button(theme_label, on_click=toggle_theme, use_container_width=True)

# --- MAIN TWO-COLUMN LAYOUT ---
col_form, col_results = st.columns([5, 7])

# --- DYNAMIC CLIENT-SIDE METRICS CALCULATIONS ---
# We track current values to display them before sending to server
with col_form:
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.subheader("Client Details")
    st.write("Provide parameters below to calculate lifestyle factors and predict premium category.")

    with st.form("client_form", clear_on_submit=False):
        age = st.slider("Age (Years)", min_value=1, max_value=119, value=30, step=1)
        
        c_wt, c_ht = st.columns(2)
        with c_wt:
            weight = st.number_input("Weight (kg)", min_value=50.1, max_value=599.9, value=75.0, step=0.1, format="%.1f")
        with c_ht:
            height = st.number_input("Height (meters)", min_value=0.5, max_value=2.5, value=1.75, step=0.01, format="%.2f")
            
        c_inc, c_smoke = st.columns([2, 1])
        with c_inc:
            income_lpa = st.number_input("Annual Income (Lakhs LPA)", min_value=0.0, max_value=1000.0, value=12.5, step=0.1, format="%.1f")
        with c_smoke:
            st.write("") # vertical spacing helper
            st.write("")
            smoker = st.checkbox("Smoker status", value=False)
            
        city = st.selectbox("City", options=all_suggested_cities, index=all_suggested_cities.index("Bangalore") if "Bangalore" in all_suggested_cities else 0)
        
        occupation_label = st.selectbox("Occupation", options=list(occupation_map.keys()), index=list(occupation_map.keys()).index("Private Job"))
        
        submit_btn = st.form_submit_button("Predict Premium Category", use_container_width=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

# Calculations for dynamic metrics
bmi = round(weight / (height ** 2), 2)

# BMI category logic for badge styling
if bmi < 18.5:
    bmi_category = "Underweight"
    bmi_badge_cls = "badge-warning"
elif bmi < 25:
    bmi_category = "Healthy"
    bmi_badge_cls = "badge-success"
elif bmi < 30:
    bmi_category = "Overweight"
    bmi_badge_cls = "badge-warning"
else:
    bmi_category = "Obese"
    bmi_badge_cls = "badge-error"

# Age group calculation
if age < 25:
    age_group_val = "Young"
elif age < 45:
    age_group_val = "Adult"
elif age < 60:
    age_group_val = "Middle Aged"
else:
    age_group_val = "Senior"

# Lifestyle Risk calculation
if smoker and bmi > 30:
    lifestyle_risk_val = "High"
    risk_badge_cls = "badge-error"
elif smoker or bmi > 27:
    lifestyle_risk_val = "Medium"
    risk_badge_cls = "badge-warning"
else:
    lifestyle_risk_val = "Low"
    risk_badge_cls = "badge-success"

# City Tier calculation
if city in tier_1_cities:
    city_tier_val = 1
elif city in tier_2_cities:
    city_tier_val = 2
else:
    city_tier_val = 3

# --- RESULTS COLUMN ---
with col_results:
    # 1. Predictions display
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.subheader("Prediction Dashboard")
    
    if submit_btn:
        with st.spinner("Analyzing risk profile and querying prediction engine..."):
            # Call FastAPI
            api_url = "http://127.0.0.1:8000/predict"
            payload = {
                "age": age,
                "weight": weight,
                "height": height,
                "income_lpa": income_lpa,
                "smoker": smoker,
                "city": city,
                "occupation": occupation_map[occupation_label]
            }
            
            try:
                response = requests.post(api_url, json=payload, timeout=5)
                if response.status_code == 200:
                    pred_data = response.json()
                    prediction = pred_data.get("prediction", "Unknown")
                    
                    # Style prediction output
                    result_color_cls = "result-low" if prediction == "Low" else ("result-medium" if prediction == "Medium" else "result-high")
                    
                    st.markdown(f"""
                    <div class="predict-box">
                        <div class="predict-title">Calculated Insurance Premium Category</div>
                        <div class="predict-result {result_color_cls}">{prediction}</div>
                        <p style="font-size: 0.85rem; color: {TEXT_MUTED}; margin: 0;">
                            Prediction served from model.pkl backend API.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"Prediction API returned error: Code {response.status_code}. Detail: {response.text}")
            except requests.exceptions.ConnectionError:
                st.warning("⚠️ Prediction Engine Unreachable")
                st.markdown(f"""
                <div class="predict-box" style="border-color: {AMBER_COLOR}; background: {AMBER_MUTED}; text-align: left;">
                    <div style="font-weight: 700; color: {AMBER_COLOR}; margin-bottom: 0.5rem;">FastAPI Backend is Down</div>
                    <p style="margin: 0; font-size: 0.85rem; color: {TEXT_COLOR};">
                        The frontend cannot connect to the backend server at <code>http://127.0.0.1:8000</code>.
                    </p>
                    <div style="margin-top: 0.8rem; font-size: 0.8rem; font-family: 'JetBrains Mono', monospace; color: {TEXT_MUTED};">
                        Please run the backend model first:<br>
                        <span style="color: {TEXT_COLOR};">venv\\Scripts\\activate</span><br>
                        <span style="color: {TEXT_COLOR};">uvicorn app:app --reload</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
    else:
        st.info("👈 Enter details in the form and click 'Predict Premium Category' to see results.")
        
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. Dynamic client-side metrics cards
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.subheader("Calculated Risk Profile Metrics")
    st.write("These metrics are computed instantly based on your current inputs before model evaluation.")

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">Computed BMI</div>
            <div class="metric-value">{bmi}</div>
            <span class="metric-badge {bmi_badge_cls}">{bmi_category}</span>
        </div>
        <div class="metric-card">
            <div class="metric-label">Age Group</div>
            <div class="metric-value">{age_group_val}</div>
            <span class="metric-badge badge-info">Tier Group</span>
        </div>
        <div class="metric-card">
            <div class="metric-label">Lifestyle Risk</div>
            <div class="metric-value">{lifestyle_risk_val}</div>
            <span class="metric-badge {risk_badge_cls}">{lifestyle_risk_val} Risk</span>
        </div>
        <div class="metric-card">
            <div class="metric-label">City Classification</div>
            <div class="metric-value">Tier {city_tier_val}</div>
            <span class="metric-badge badge-info">{"Tier 1 City" if city_tier_val==1 else ("Tier 2 City" if city_tier_val==2 else "Tier 3 City")}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- INTERACTIVE ANALYTICS PLOTS ---
st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
st.markdown("""
    <div class="chart-title">Population Distribution Analysis</div>
    <div class="chart-subtitle">Compare client features against historical database distribution</div>
""", unsafe_allow_html=True)

plot_col1, plot_col2 = st.columns(2)

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#fafafa" if IS_DARK else "#09090b", size=11),
    margin=dict(l=40, r=20, t=25, b=40),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.06)" if IS_DARK else "rgba(0,0,0,0.06)",
        zerolinecolor="rgba(255,255,255,0.06)" if IS_DARK else "rgba(0,0,0,0.06)",
        tickfont=dict(size=10, color="#71717a"),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.06)" if IS_DARK else "rgba(0,0,0,0.06)",
        zerolinecolor="rgba(255,255,255,0.06)" if IS_DARK else "rgba(0,0,0,0.06)",
        tickfont=dict(size=10, color="#71717a"),
    ),
    legend=dict(
        font=dict(size=10),
        bgcolor="rgba(0,0,0,0)",
    )
)

with plot_col1:
    # BMI comparison plot
    fig_bmi = px.histogram(
        df_history, 
        x="bmi", 
        nbins=20,
        title="BMI Distribution & Current Client",
        color_discrete_sequence=["#2563eb"],
        opacity=0.65
    )
    # Add vertical line for user BMI
    fig_bmi.add_vline(x=bmi, line_width=3, line_dash="dash", line_color="#ef4444", annotation_text=f"Current: {bmi}")
    fig_bmi.update_layout(
        **PLOT_LAYOUT,
        xaxis_title="Body Mass Index (BMI)",
        yaxis_title="Count of Individuals"
    )
    st.plotly_chart(fig_bmi, use_container_width=True, config={"displayModeBar": False})

with plot_col2:
    # Income comparison plot
    fig_inc = px.histogram(
        df_history, 
        x="income_lpa", 
        nbins=20,
        title="Income Distribution & Current Client",
        color_discrete_sequence=["#10b981"],
        opacity=0.65
    )
    # Add vertical line for user Income
    fig_inc.add_vline(x=income_lpa, line_width=3, line_dash="dash", line_color="#ef4444", annotation_text=f"Current: {income_lpa}")
    fig_inc.update_layout(
        **PLOT_LAYOUT,
        xaxis_title="Annual Income (Lakhs LPA)",
        yaxis_title="Count of Individuals"
    )
    st.plotly_chart(fig_inc, use_container_width=True, config={"displayModeBar": False})

st.markdown('</div>', unsafe_allow_html=True)
