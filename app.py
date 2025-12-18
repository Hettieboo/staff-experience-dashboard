import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Staff Experience Cross Analysis",
    layout="wide"
)

st.title("Staff Experience & Job Fulfillment – Cross Analysis")
st.markdown(
    """
    This dashboard examines whether demographic and organizational factors
    influence **job fulfillment and staff experience** at Homes First.
    """
)

# --------------------------------------------------
# LOAD DATA (FROM REPO)
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("Combined- Cross Analysis.xlsx")
    df = df.fillna("No response")
    return df

df = load_data()

# --------------------------------------------------
# COLUMN DEFINITIONS
# --------------------------------------------------
role_col = "Select the role/department that best describes your current position at Homes First."
race_col = "Which racial or ethnic identity/identities best reflect you. (Select all that apply.)"
disability_col = "Do you identify as an individual living with a disabili... disability/disabilities do you have? (Select all that apply.)"

fulfillment_col = "How fulfilling and rewarding do you find your work?"
recommend_col = "How likely are you to recommend Homes First as a good place to work?"
recognition_col = "Do you feel you get acknowledged and recognized for your contribution  at work?"
growth_col = "Do you feel there is potential for growth at Homes First?"

# --------------------------------------------------
# KPI CALCULATIONS (SAFE STRING HANDLING)
# --------------------------------------------------
st.header("Key Staff Experience Indicators")

total_responses = len(df)

high_fulfillment = (
    df[fulfillment_col]
    .astype(str)
    .str.contains("Very|Extremely", case=False, na=False)
    .sum()
)

recommend_positive = (
    df[recommend_col]
    .astype(str)
    .str.contains("Very|Extremely|Likely", case=False, na=False)
    .sum()
)

growth_positive = (
    df[growth_col]
    .astype(str)
    .str.contains("Yes", case=False, na=False)
    .sum()
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Responses", total_responses)

col2.metric(
    "High Job Fulfillment",
    high_fulfillment,
    f"{high_fulfillment / total_responses:.0%}"
)

col3.metric(
    "Would Recommend Homes First",
    recommend_positive,
    f"{recommend_positive / total_responses:.0%}"
)

col4.metric(
    "Perceived Growth Opportunities",
    growth_positive,
    f"{growth_positive / total_responses:.0%}"
)

# --------------------------------------------------
# CROSS-ANALYSIS FUNCTION
# --------------------------------------------------
def cross_analysis(factor_col, title):
    st.subheader(title)

    cross_tab = (
        pd.crosstab(
            df[factor_col].astype(str),
            df[fulfillment_col].astype(str),
            normalize="index"
        ) * 100
    ).round(1)

    st.dataframe(cross_tab)

    fig, ax = plt.subplots()
    cross_tab.plot(kind="bar", stacked=True, ax=ax)
    ax.set_ylabel("Percentage (%)")
    ax.set_xlabel("")
    ax.set_title("Distribution of Job Fulfillment")
    plt.xticks(rotation=45, ha="right")

    st.pyplot(fig)

# --------------------------------------------------
# CROSS-ANALYSIS SECTIONS
# --------------------------------------------------
st.header("Cross Analysis Results")

cross_analysis(role_col, "Job Fulfillment by Role / Department")
cross_analysis(race_col, "Job Fulfillment by Race / Ethnicity")
cross_analysis(disability_col, "Job Fulfillment by Disability Status")

# --------------------------------------------------
# EXPERIENCE DRIVERS
# --------------------------------------------------
st.header("Key Drivers of Staff Experience")

driver_map = {
    "Recognition at Work": recognition_col,
    "Growth Opportunities": growth_col,
    "Likelihood to Recommend": recommend_col,
}

for label, col in driver_map.items():
    st.subheader(label)

    breakdown = (
        df[col]
        .astype(str)
        .value_counts(normalize=True) * 100
    ).round(1)

    st.dataframe(breakdown)

# --------------------------------------------------
# INSIGHTS & RECOMMENDATIONS
# --------------------------------------------------
st.header("Insights & Recommendations")

st.markdown(
    """
### Key Insights
- Job fulfillment varies significantly across **roles and departments**,
  suggesting operational context strongly shapes staff experience.
- Perceived **career growth opportunities** are closely linked to
  higher fulfillment and stronger advocacy for the organization.
- Differences across **race, ethnicity, and disability status**
  indicate uneven staff experiences that may reflect systemic or
  accessibility-related factors.
- Recognition and acknowledgment consistently emerge as
  strong drivers of positive sentiment.

### Recommendations
**1. Role-Specific Engagement Strategies**  
Target roles with lower fulfillment for workload review, management support,
and tailored engagement initiatives.

**2. Strengthen Career Pathways**  
Clearly communicate advancement opportunities, professional development
options, and internal mobility pathways.

**3. Formalize Recognition Mechanisms**  
Introduce consistent, organization-wide recognition practices to ensure
visibility of staff contributions.

**4. Deepen Equity & Inclusion Efforts**  
Conduct qualitative follow-ups with under-represented groups to identify
barriers impacting experience and fulfillment.

**5. Monitor Progress Over Time**  
Use this dashboard longitudinally to assess whether interventions lead to
measurable improvements in staff experience.
"""
)

st.caption("This analysis supports evidence-based people and culture decision-making.")
