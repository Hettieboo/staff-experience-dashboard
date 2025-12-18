import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Staff Experience Cross Analysis",
    layout="wide"
)

st.title("Staff Experience & Job Fulfillment – Cross Analysis")
st.markdown(
    """
    This dashboard analyzes how **demographic and organizational factors**
    influence **job fulfillment and staff experience** at Homes First.
    """
)

# -------------------------------
# LOAD DATA
# -------------------------------
@st.cache_data
def load_data():
    return pd.read_excel("Combined- Cross Analysis.xlsx")

df = load_data()

# -------------------------------
# COLUMN MAPPING
# -------------------------------
role_col = "Select the role/department that best describes your current position at Homes First."
race_col = "Which racial or ethnic identity/identities best reflect you. (Select all that apply.)"
disability_col = "Do you identify as an individual living with a disabili... disability/disabilities do you have? (Select all that apply.)"

fulfillment_col = "How fulfilling and rewarding do you find your work?"
recommend_col = "How likely are you to recommend Homes First as a good place to work?"
recognition_col = "Do you feel you get acknowledged and recognized for your contribution  at work?"
growth_col = "Do you feel there is potential for growth at Homes First?"

# -------------------------------
# KPI SECTION
# -------------------------------
st.header("Key Staff Experience Indicators")

total_responses = len(df)

high_fulfillment = df[fulfillment_col].str.contains("Very|Extremely", na=False).sum()
recommend_positive = df[recommend_col].str.contains("Very|Extremely|Likely", na=False).sum()
growth_positive = df[growth_col].str.contains("Yes", na=False).sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Responses", total_responses)

col2.metric(
    "High Job Fulfillment",
    f"{high_fulfillment}",
    f"{high_fulfillment / total_responses:.0%}"
)

col3.metric(
    "Would Recommend Homes First",
    f"{recommend_positive}",
    f"{recommend_positive / total_responses:.0%}"
)

col4.metric(
    "Perceive Growth Opportunities",
    f"{growth_positive}",
    f"{growth_positive / total_responses:.0%}"
)

# -------------------------------
# FUNCTION FOR CROSS ANALYSIS
# -------------------------------
def cross_analysis(factor_col, title):
    st.subheader(title)

    cross_tab = pd.crosstab(
        df[factor_col],
        df[fulfillment_col],
        normalize="index"
    ) * 100

    st.dataframe(cross_tab.round(1))

    # Plot
    fig, ax = plt.subplots()
    cross_tab.plot(kind="bar", stacked=True, ax=ax)
    ax.set_ylabel("Percentage (%)")
    ax.set_xlabel("")
    ax.set_title("Job Fulfillment Distribution")
    plt.xticks(rotation=45, ha="right")

    st.pyplot(fig)

# -------------------------------
# CROSS ANALYSIS SECTIONS
# -------------------------------
st.header("Cross Analysis")

cross_analysis(role_col, "Job Fulfillment by Role / Department")
cross_analysis(race_col, "Job Fulfillment by Race / Ethnicity")
cross_analysis(disability_col, "Job Fulfillment by Disability Status")

# -------------------------------
# EXPERIENCE DRIVERS
# -------------------------------
st.header("Key Experience Drivers")

driver_cols = {
    "Recognition at Work": recognition_col,
    "Growth Opportunities": growth_col,
    "Recommendation Likelihood": recommend_col
}

for label, col in driver_cols.items():
    st.subheader(label)
    breakdown = df[col].value_counts(normalize=True) * 100
    st.dataframe(breakdown.round(1))

# -------------------------------
# INSIGHTS & RECOMMENDATIONS
# -------------------------------
st.header("Insights & Recommendations")

st.markdown(
    """
    ### Key Insights
    - Job fulfillment varies noticeably across **roles and departments**, indicating that
      day-to-day work context plays a strong role in staff experience.
    - Perceived **growth opportunities** strongly align with higher fulfillment
      and willingness to recommend Homes First as a workplace.
    - Differences across **race/ethnicity and disability status** suggest that
      staff experience is not uniform and may be influenced by inclusion,
      accessibility, and representation factors.
    - Recognition and acknowledgment at work are consistent predictors
      of positive staff sentiment.
    
    ### Recommendations
    **1. Target Role-Specific Interventions**  
    Focus engagement, workload balancing, and career development initiatives
    on roles showing lower fulfillment levels.

    **2. Strengthen Career Pathways**  
    Clearly communicate growth opportunities, internal mobility options,
    and professional development programs.

    **3. Enhance Recognition Practices**  
    Implement structured recognition mechanisms to ensure contributions
    are consistently acknowledged across teams.

    **4. Advance Equity & Inclusion Efforts**  
    Conduct deeper qualitative follow-ups with under-represented groups
    to understand barriers affecting fulfillment and experience.

    **5. Monitor Continuously**  
    Use this dashboard as a recurring monitoring tool to track improvements
    over time and evaluate the impact of interventions.
    """
)

st.caption("Data-driven insights to support strategic HR and people-experience decisions.")
