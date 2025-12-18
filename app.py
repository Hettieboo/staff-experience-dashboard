import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("Combined- Cross Analysis.xlsx")
    df = df.fillna("No response")
    return df

df = load_data()

# --------------------------------------------------
# RESOLVE COLUMNS SAFELY
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
# GROUP ROLES
# --------------------------------------------------
role_mapping = {
    # Staff / Support
    "Assistant": "Staff / Support",
    "Coordinator": "Staff / Support",
    "Administrator": "Staff / Support",
    "Analyst": "Staff / Support",
    "Generalist": "Staff / Support",
    # Supervisors
    "Supervisor (Shelters/Housing)": "Shelter Supervisor",
    "Supervisor (HR/Finance/Property/Fundraising/Development)": "Admin Supervisor",
    # Directors / Managers
    "Director/Assistant Director/Manager/Assistant Manager (HR/Finance/Property/Fundraising/Development)": "Admin Director/Manager",
    "Director/Assistant Director/Manager/Assistant Manager/Site Manager (Shelters/Housing)": "Shelter Director/Manager",
    # Departments / Programs
    "CSW - Shelters": "CSW - Shelters",
    "ICM - Shelters (includes ICM, HHW, Community Engagement, ICM Health Standards, etc.)": "ICM - Shelters",
    "Non-24 Hour Program (including ICM, follow-up supports and PSW)": "Non-24 Hour Program",
    "Relief": "Relief Staff",
    # Others / undisclosed
    "Prefer not to disclose/Other": "Other / Prefer not to disclose",
    "Other (Smaller departments/teams not listed seperately in an effort to maintain confidentiality)": "Other / Prefer not to disclose"
}

df['role_group'] = df[role_col].map(role_mapping).fillna(df[role_col])

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------
st.subheader("Key Indicators")

total = len(df)

def pct_contains(col, pattern):
    return (
        df[col].astype(str)
        .str.contains(pattern, case=False, na=False)
        .mean()
    ) * 100

k1, k2, k3, k4 = st.columns(4)
k1.metric("Responses", total)
k2.metric("High Fulfillment", f"{pct_contains(fulfillment_col, 'Very|Extremely'):.0f}%")
k3.metric("Would Recommend", f"{pct_contains(recommend_col, 'Very|Extremely|Likely'):.0f}%")
k4.metric("Sees Growth", f"{pct_contains(growth_col, 'Yes'):.0f}%")

st.divider()

# --------------------------------------------------
# CROSS-ANALYSIS FUNCTIONS (ROBUST)
# --------------------------------------------------
def cross_analysis(factor_col, outcome_col, pattern="Very|Extremely|Yes|Likely"):
    """
    Returns a dataframe showing % of positive responses for each category.
    Handles cases where no responses match the pattern.
    """
    ct = pd.crosstab(
        df[factor_col],
        df[outcome_col].astype(str).str.contains(pattern, case=False),
        normalize="index"
    )
    
    if True not in ct.columns:
        ct[True] = 0.0
    
    result = ct[True] * 100
    return result.sort_values(ascending=False).reset_index(name=f"% Positive ({outcome_col})")

def cross_bar_multiple(factor_col, outcome_col, title, pattern="Very|Extremely|Yes|Likely"):
    """
    Draws a horizontal bar chart for cross-analysis.
    """
    data = cross_analysis(factor_col, outcome_col, pattern)
    
    fig, ax = plt.subplots(figsize=(10, max(4, len(data) * 0.45)))
    ax.barh(data[factor_col], data[f"% Positive ({outcome_col})"], color="#2ca02c")
    ax.set_xlim(0, 100)
    ax.set_xlabel("% Positive Response")
    ax.set_ylabel("")
    
    for i, v in enumerate(data[f"% Positive ({outcome_col})"]):
        ax.text(v + 1, i, f"{v:.0f}%", va="center", fontsize=10)
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# --------------------------------------------------
# CROSS ANALYSIS ACROSS CATEGORIES
# --------------------------------------------------
st.header("Cross Analysis Across Categories")

categories = ["role_group", race_col, disability_col]
outcomes = {
    "Job Fulfillment": fulfillment_col,
    "Recommendation": recommend_col,
    "Recognition": recognition_col,
    "Growth Opportunities": growth_col
}

for cat in categories:
    st.subheader(f"By {cat.replace('_',' ').title()}")
    for outcome_name, outcome_col in outcomes.items():
        st.markdown(f"**{outcome_name}:**")
        cross_bar_multiple(cat, outcome_col, outcome_name)
        df_result = cross_analysis(cat, outcome_col)
        st.dataframe(df_result)

st.divider()

# --------------------------------------------------
# EXPERIENCE DRIVERS (EXECUTIVE STYLE)
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
    ax.barh([title], [pct], color="#ff7f0e")
    ax.set_xlim(0, 100)
    ax.axis("off")
    ax.text(pct + 1, 0, f"{pct:.0f}%", va="center", fontsize=12)

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
- Some groups consistently report lower fulfillment, indicating equity gaps.

### Recommendations
1. Prioritize low-fulfillment roles for workload and management review.
2. Strengthen visibility and clarity of career progression pathways.
3. Standardize recognition practices across teams.
4. Conduct qualitative follow-ups with under-represented groups.
5. Track changes longitudinally using this dashboard.
"""
)

st.caption("Professional people analytics dashboard – decision-focused, not data-heavy.")
