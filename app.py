import streamlit as st
import pandas as pd
import plotly.express as px

# --- Load data ---
@st.cache_data
def load_data():
    df = pd.read_excel("homes_first_survey.xlsx")
    return df

df = load_data()
st.set_page_config(page_title="Staff Experience Dashboard", layout="wide")

# --- Header ---
st.title("Staff Experience & Job Fulfillment")
st.markdown("""
Cross-analysis of organizational and demographic factors influencing staff experience.
""")

# --- Key Indicators ---
total_responses = len(df)
high_fulfillment = (df["How fulfilling and rewarding do you find your work?"].str.contains("extremely|some parts")).mean() * 100
would_recommend = (df["How likely are you to recommend Homes First as a good place to work?"] >= 8).mean() * 100
sees_growth = (df["Do you feel there is potential for growth at Homes First?"].str.contains("Yes")).mean() * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Responses", total_responses)
col2.metric("High Fulfillment", f"{high_fulfillment:.0f}%")
col3.metric("Would Recommend", f"{would_recommend:.0f}%")
col4.metric("Sees Growth", f"{sees_growth:.0f}%")

st.markdown("---")

# --- Function for clean cross analysis charts ---
def cross_analysis(factor_col, outcome_col, question_title, positive_responses=None):
    st.markdown(f"<div style='background-color:#F0F2F6;padding:5px 10px;border-radius:5px;font-weight:bold'>{question_title}</div>", unsafe_allow_html=True)
    
    if positive_responses:
        df_filtered = df[df[outcome_col].isin(positive_responses)]
        ct = df_filtered.groupby(factor_col).size().reset_index(name='Count')
        ct['Percentage'] = ct['Count'] / ct['Count'].sum() * 100
    else:
        ct = df[outcome_col].value_counts(normalize=True).reset_index()
        ct.columns = [factor_col, 'Percentage']
        ct['Percentage'] *= 100

    fig = px.bar(
        ct,
        x=factor_col,
        y='Percentage',
        text=ct['Percentage'].round(1),
        height=350
    )
    fig.update_traces(marker_color="#FF6361", textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, margin=dict(l=20, r=20, t=30, b=70))
    st.plotly_chart(fig, use_container_width=True)

# --- Cross Analysis Examples ---
# By Role
cross_analysis(
    "Select the role/department that best describes your current position at Homes First.",
    "How fulfilling and rewarding do you find your work?",
    "Job Fulfillment",
    positive_responses=[
        "I find the work I do extremely fulfilling and rewarding",
        "I find the work I do fulfilling and rewarding in some parts and not so much in others"
    ]
)

cross_analysis(
    "Select the role/department that best describes your current position at Homes First.",
    "How likely are you to recommend Homes First as a good place to work?",
    "Recommendation",
    positive_responses=[8,9,10]
)

cross_analysis(
    "Select the role/department that best describes your current position at Homes First.",
    "Do you feel you get acknowledged and recognized for your contribution  at work?",
    "Recognition",
    positive_responses=[
        "Yes, I do feel recognized and acknowledged",
        "I somewhat feel recognized and acknowledged"
    ]
)

cross_analysis(
    "Select the role/department that best describes your current position at Homes First.",
    "Do you feel there is potential for growth at Homes First?",
    "Growth Opportunities",
    positive_responses=["Yes, I do feel there is potential to grow"]
)

st.markdown("---")
# --- You can repeat cross_analysis for other categories (Race/Ethnicity, Disability) ---
