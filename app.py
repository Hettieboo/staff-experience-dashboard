import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Staff Experience Cross Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Staff Experience & Job Fulfillment – Cross Analysis")
st.markdown(
    """
    This dashboard examines whether demographic and organizational factors
    influence **job fulfillment and staff experience** at Homes First.
    """
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("Combined- Cross Analysis.xlsx")
    return df.fillna("No response")

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ 'Combined- Cross Analysis.xlsx' not found in the repo.")
    st.stop()

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
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("🔍 Filters")

roles = ["All"] + sorted(df[role_col].unique())
selected_role = st.sidebar.selectbox("Filter by Role / Department", roles)

filtered_df = df.copy()
if selected_role != "All":
    filtered_df = filtered_df[filtered_df[role_col] == selected_role]

st.sidebar.metric("Filtered Responses", len(filtered_df))

if filtered_df.empty:
    st.warning("No data available for selected filters.")
    st.stop()

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------
st.header("📈 Key Staff Experience Indicators")

total = len(filtered_df)

def pct(condition):
    return f"{condition.sum() / total:.0%}"

high_fulfillment = filtered_df[fulfillment_col].astype(str).str.contains("Very|Extremely", case=False)
recommend_positive = filtered_df[recommend_col].astype(str).str.contains("Very|Extremely|Likely", case=False)
growth_positive = filtered_df[growth_col].astype(str).str.contains("Yes", case=False)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Responses", total)
col2.metric("😊 High Fulfillment", pct(high_fulfillment), f"{high_fulfillment.sum()} respondents")
col3.metric("👍 Would Recommend", pct(recommend_positive), f"{recommend_positive.sum()} respondents")
col4.metric("📈 Growth Potential", pct(growth_positive), f"{growth_positive.sum()} respondents")

# --------------------------------------------------
# CROSS ANALYSIS FUNCTION
# --------------------------------------------------
def cross_analysis(factor_col, title, data):
    st.subheader(title)

    cross_tab = pd.crosstab(
        data[factor_col].astype(str),
        data[fulfillment_col].astype(str),
        normalize="index"
    ) * 100

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(cross_tab.columns)))

    cross_tab.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        color=colors
    )

    ax.set_ylabel("Percentage (%)")
    ax.set_title("Job Fulfillment Distribution")
    ax.legend(title="Fulfillment Level", bbox_to_anchor=(1.05, 1))
    ax.set_ylim(0, 100)

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.dataframe(cross_tab.round(1), use_container_width=True)

# --------------------------------------------------
# CROSS ANALYSIS SECTIONS
# --------------------------------------------------
st.header("🔄 Cross Analysis Results")

cross_analysis(role_col, "Job Fulfillment by Role / Department", filtered_df)
st.divider()
cross_analysis(race_col, "Job Fulfillment by Race / Ethnicity", filtered_df)
st.divider()
cross_analysis(disability_col, "Job Fulfillment by Disability Status", filtered_df)

# --------------------------------------------------
# CORRELATION MATRIX (NO SEABORN)
# --------------------------------------------------
st.header("🔗 Experience Factor Correlations")

binary_df = pd.DataFrame({
    "High Fulfillment": high_fulfillment.astype(int),
    "Would Recommend": recommend_positive.astype(int),
    "Recognized": filtered_df[recognition_col].astype(str).str.contains("Yes", case=False).astype(int),
    "Growth Potential": growth_positive.astype(int)
})

corr = binary_df.corr()

fig, ax = plt.subplots(figsize=(8, 6))
cax = ax.matshow(corr, cmap="RdYlGn", vmin=-1, vmax=1)

plt.xticks(range(len(corr.columns)), corr.columns, rotation=45, ha="left")
plt.yticks(range(len(corr.columns)), corr.columns)

for i in range(len(corr.columns)):
    for j in range(len(corr.columns)):
        ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center")

fig.colorbar(cax)
plt.tight_layout()
st.pyplot(fig)
plt.close()

# --------------------------------------------------
# INSIGHTS & RECOMMENDATIONS
# --------------------------------------------------
st.header("💡 Insights & Recommendations")

st.markdown("""
### Key Insights
- Job fulfillment varies by **role, race, and disability status**
- **Growth and recognition** are strongly correlated with fulfillment
- Recommendation likelihood tracks closely with positive experience

### Recommendations
1. Address role-specific experience gaps
2. Strengthen internal growth pathways
3. Standardize recognition practices
4. Conduct qualitative DEI follow-ups
5. Track trends longitudinally
""")

st.caption("📊 Evidence-based people analytics dashboard")
