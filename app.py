import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import numpy as np

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Staff Experience & Job Fulfillment",
    layout="wide"
)

st.title("Staff Experience & Job Fulfillment")
st.markdown(
    "Cross-analysis of organizational and demographic factors influencing staff experience."
)

# --------------------------------------------------
# BRAND COLOURS
# --------------------------------------------------
PRIMARY_COLOR = "#FF6B81"  # pink
SECONDARY_COLOR = "#4B4B4B"  # grey/dark
ACCENT_COLOR = "#FFA500"  # optional accent

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("Combined- Cross Analysis.xlsx")
    df = df.fillna("No response")
    return df

df = load_data()

# --------------------------------------------------
# SAFE COLUMN RESOLUTION
# --------------------------------------------------
def find_col(keyword):
    return next(col for col in df.columns if keyword.lower() in col.lower())

role_col = find_col("role")
race_col = find_col("racial")
disability_col = find_col("disabili")
fulfillment_col = find_col("fulfilling")
recommend_col = find_col("recommend")
recognition_col = find_col("recognized")
growth_col = find_col("growth")

# --------------------------------------------------
# KPI FUNCTION
# --------------------------------------------------
total = len(df)

def pct_contains(col, pattern):
    return (df[col].astype(str).str.contains(pattern, case=False, na=False).mean()) * 100

# --------------------------------------------------
# FULFILLMENT INDEX
# --------------------------------------------------
def fulfillment_index(col):
    mapping = {'Extremely': 2, 'Very': 2, 'Somewhat': 1, 'No response': 0, 'No': 0}
    return df[col].map(lambda x: next((v for k,v in mapping.items() if k.lower() in str(x).lower()), 0)).mean() * 50

fi_score = fulfillment_index(fulfillment_col)

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------
st.subheader("Key Indicators")
k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Responses", total)
k2.metric("High Fulfillment", f"{pct_contains(fulfillment_col, 'Very|Extremely'):.0f}%")
k3.metric("Would Recommend", f"{pct_contains(recommend_col, 'Very|Extremely|Likely'):.0f}%")
k4.metric("Sees Growth", f"{pct_contains(growth_col, 'Yes'):.0f}%")
k5.metric("Fulfillment Index", f"{fi_score:.0f}/100")

st.divider()

# --------------------------------------------------
# CROSS ANALYSIS FUNCTION
# --------------------------------------------------
def cross_bar(factor_col, title):
    st.subheader(title)

    data = (
        pd.crosstab(
            df[factor_col],
            df[fulfillment_col].astype(str).str.contains("Very|Extremely", case=False),
            normalize="index"
        )[True] * 100
    ).sort_values()

    fig, ax = plt.subplots(figsize=(10, max(4, len(data) * 0.6)))

    ax.barh(data.index, data.values, color=PRIMARY_COLOR)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Percent reporting high fulfillment", fontsize=11, color=SECONDARY_COLOR)
    ax.set_ylabel("")
    ax.set_title("", fontsize=12, weight='bold')

    for i, v in enumerate(data.values):
        ax.text(v + 1, i, f"{v:.0f}%", va="center", fontsize=10, color=SECONDARY_COLOR)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# --------------------------------------------------
# CROSS ANALYSIS SECTIONS
# --------------------------------------------------
st.header("Cross Analysis")

cross_bar(role_col, "Job Fulfillment by Role / Department")
cross_bar(race_col, "Job Fulfillment by Race / Ethnicity")
cross_bar(disability_col, "Job Fulfillment by Disability Status")

st.divider()

# --------------------------------------------------
# EXPERIENCE DRIVERS
# --------------------------------------------------
st.header("Key Experience Drivers")

driver_cols = {
    "Recognition at Work": recognition_col,
    "Growth Opportunities": growth_col,
    "Likelihood to Recommend": recommend_col
}

for title, col in driver_cols.items():
    pct = pct_contains(col, "Yes|Likely|Very|Extremely")

    fig, ax = plt.subplots(figsize=(6, 1.8))
    ax.barh([title], [pct], color=PRIMARY_COLOR)
    ax.set_xlim(0, 100)
    ax.axis("off")
    ax.text(pct + 1, 0, f"{pct:.0f}%", va="center", fontsize=12, color=SECONDARY_COLOR)

    st.pyplot(fig)
    plt.close()

st.divider()

# --------------------------------------------------
# INSIGHTS & RECOMMENDATIONS
# --------------------------------------------------
st.header("Insights & Recommendations")

st.markdown(
    """
### Key Insights
- Job fulfillment varies meaningfully across roles and identity groups.
- Growth perception and recognition are the strongest drivers of positive experience.
- Some demographic groups consistently report lower fulfillment, indicating equity gaps.

### Recommendations
1. Prioritise low-fulfillment roles for workload and management review.
2. Strengthen visibility and clarity of career progression pathways.
3. Standardise recognition practices across teams.
4. Conduct qualitative follow-ups with under-represented groups.
5. Track changes longitudinally using this dashboard.
"""
)

st.caption("Professional people analytics dashboard – decision-focused, not data-heavy.")

# --------------------------------------------------
# PDF EXPORT FUNCTION
# --------------------------------------------------
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Staff Experience & Fulfillment Report", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Total Responses: {total}", ln=True)
    pdf.cell(200, 10, txt=f"Fulfillment Index: {fi_score:.0f}/100", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 8, txt="Insights:\n- Job fulfillment varies by role and demographic.\n- Growth and recognition are key drivers.\n\nRecommendations:\n- Prioritize low-fulfillment roles, standardize recognition, track progress.")
    pdf_output = "fulfillment_report.pdf"
    pdf.output(pdf_output)
    return pdf_output

st.download_button("Download PDF Summary", generate_pdf())

# --------------------------------------------------
# OPTIONAL: EMBED OPTIMISATION FOR WEBFLOW
# --------------------------------------------------
st.markdown(
    """
<style>
.css-18e3th9 {padding-top: 1rem;}
.css-1d391kg {padding: 0rem;}
</style>
""",
    unsafe_allow_html=True
)
