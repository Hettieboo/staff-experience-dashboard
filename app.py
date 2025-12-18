# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="Staff Experience & Job Fulfillment",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("homes_first_survey.csv")  # Update path if needed
    return df

df = load_data()

# -----------------------------
# ROLE GROUP MAPPING
# -----------------------------
role_mapping = {
    "Assistant": "Staff / Support",
    "Coordinator": "Staff / Support",
    "Administrator": "Staff / Support",
    "Analyst": "Staff / Support",
    "Generalist": "Staff / Support",
    "Supervisor (Shelters/Housing)": "Shelter Supervisor",
    "Supervisor (HR/Finance/Property/Fundraising/Development)": "Admin Supervisor",
    "Director/Assistant Director/Manager/Assistant Manager (HR/Finance/Property/Fundraising/Development)": "Admin Director/Manager",
    "Director/Assistant Director/Manager/Assistant Manager/Site Manager (Shelters/Housing)": "Shelter Director/Manager",
    "CSW - Shelters": "CSW - Shelters",
    "ICM - Shelters (includes ICM, HHW, Community Engagement, ICM Health Standards, etc.)": "ICM - Shelters",
    "Non-24 Hour Program (including ICM, follow-up supports and PSW)": "Non-24 Hour Program",
    "Relief": "Relief Staff",
    "Prefer not to disclose/Other": "Other / Prefer not to disclose",
    "Other (Smaller departments/teams not listed seperately in an effort to maintain confidentiality)": "Other / Prefer not to disclose"
}

df["Role Group"] = df["Select the role/department that best describes your current position at Homes First."].map(role_mapping)

# -----------------------------
# RESPONSE MAPPING
# -----------------------------
def map_fulfillment(response):
    response = str(response).lower()
    if "extremely fulfilling" in response or "fulfilling and rewarding in some parts" in response or "somewhat fulfilling" in response:
        return True
    else:
        return False

def map_recommendation(response):
    try:
        value = int(response)
        return value >= 8  # 8, 9, 10 considered positive
    except:
        response = str(response).lower()
        return "yes" in response

def map_recognition(response):
    response = str(response).lower()
    if "yes" in response or "somewhat feel recognized" in response or "i do find myself being recognized" in response:
        return True
    else:
        return False

def map_growth(response):
    response = str(response).lower()
    if "yes" in response or "some potential" in response:
        return True
    else:
        return False

# Apply mappings
df["High Fulfillment"] = df["How fulfilling and rewarding do you find your work?"].apply(map_fulfillment)
df["Would Recommend"] = df["How likely are you to recommend Homes First as a good place to work?"].apply(map_recommendation)
df["Recognition"] = df["Do you feel you get acknowledged and recognized for your contribution  at work?"].apply(map_recognition)
df["Sees Growth"] = df["Do you feel there is potential for growth at Homes First?"].apply(map_growth)

# -----------------------------
# CROSS ANALYSIS FUNCTION
# -----------------------------
def cross_analysis(factor_col, outcome_col):
    table = pd.crosstab(df[factor_col], df[outcome_col], normalize="index") * 100
    if True not in table.columns:
        table[True] = 0
    return table[True].reset_index(name='Percentage')

def cross_bar(factor_col, outcome_col, outcome_name):
    data = cross_analysis(factor_col, outcome_col)
    fig = px.bar(
        data,
        x=factor_col,
        y='Percentage',
        text='Percentage',
        labels={factor_col: factor_col, 'Percentage': f"% Positive {outcome_name}"},
        height=450
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# DASHBOARD
# -----------------------------
st.title("Staff Experience & Job Fulfillment")
st.markdown("""
Cross-analysis of organizational and demographic factors influencing staff experience.
""")

# Key indicators
st.subheader("Key Indicators")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Responses", df.shape[0])
col2.metric("High Fulfillment", f"{df['High Fulfillment'].mean()*100:.0f}%")
col3.metric("Would Recommend", f"{df['Would Recommend'].mean()*100:.0f}%")
col4.metric("Sees Growth", f"{df['Sees Growth'].mean()*100:.0f}%")

# Cross Analysis
st.subheader("Cross Analysis Across Categories")

categories = [
    "Role Group",
    "Which racial or ethnic identity/identities best reflect you. (Select all that apply.)",
    "Do you identify as an individual living with a disability/disabilities and if so, what type of disability/disabilities do you have? (Select all that apply.)"
]

outcomes = {
    "High Fulfillment": "Job Fulfillment",
    "Would Recommend": "Recommendation",
    "Recognition": "Recognition",
    "Sees Growth": "Growth Opportunities"
}

for cat in categories:
    st.markdown(f"### By {cat}")
    for col, label in outcomes.items():
        st.markdown(f"**{label}:**")
        cross_bar(cat, col, label)
