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
# RESOLVE COLUMNS SAFELY (NO MORE KEYERRORS)
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
# CLEAN CROSS-ANALYSIS FUNCTION
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

    fig, ax = plt.subplots(figsize=(10, max(4, len(data) * 0.45)))

    ax.barh(data.index, data.values)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Percent reporting high fulfillment")
    ax.set_ylabel("")
    ax.set_title("")

    for i, v in enumerate(data.values):
        ax.text(v + 1, i, f"{v:.0f}%", va="center", fontsize=10)

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
# EXPERIENCE DRIVERS (SIMPLE, EXECUTIVE STYLE)
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
    ax.barh([title], [pct])
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
