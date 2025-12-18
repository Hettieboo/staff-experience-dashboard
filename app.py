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
def cross_analysis(factor_col, outcome_col, question_title, positive_responses=None, column_width=1):
    st.markdown(f"<div style='background-color:#F0F2F6;padding:5px 10px;border-radius:5px;font-weight:bold;margin-bottom:5px'>{question_title}</div>", unsafe_allow_html=True)
    
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
    return fig

# --- Two-column layout ---
def display_cross_analyses(factor_col, outcome_mapping):
    for i in range(0, len(outcome_mapping), 2):
        cols = st.columns(2)
        for j in range(2):
            if i+j < len(outcome_mapping):
                outcome_col, question_title, positive_responses = outcome_mapping[i+j]
                fig = cross_analysis(factor_col, outcome_col, question_title, positive_responses)
                cols[j].plotly_chart(fig, use_container_width=True)

# --- Cross Analysis by Role ---
st.subheader("By Role Group")
role_outcomes = [
    ("How fulfilling and rewarding do you find your work?",
     "Job Fulfillment",
     ["I find the work I do extremely fulfilling and rewarding",
      "I find the work I do fulfilling and rewarding in some parts and not so much in others"]),
    ("How likely are you to recommend Homes First as a good place to work?",
     "Recommendation",
     [8,9,10]),
    ("Do you feel you get acknowledged and recognized for your contribution  at work?",
     "Recognition",
     ["Yes, I do feel recognized and acknowledged",
      "I somewhat feel recognized and acknowledged"]),
    ("Do you feel there is potential for growth at Homes First?",
     "Growth Opportunities",
     ["Yes, I do feel there is potential to grow"])
]
display_cross_analyses("Select the role/department that best describes your current position at Homes First.", role_outcomes)

st.markdown("---")

# --- Cross Analysis by Race/Ethnicity ---
st.subheader("By Racial or Ethnic Identity")
race_outcomes = [
    ("How fulfilling and rewarding do you find your work?", "Job Fulfillment",
     ["I find the work I do extremely fulfilling and rewarding",
      "I find the work I do fulfilling and rewarding in some parts and not so much in others"]),
    ("How likely are you to recommend Homes First as a good place to work?", "Recommendation", [8,9,10]),
    ("Do you feel you get acknowledged and recognized for your contribution  at work?", "Recognition",
     ["Yes, I do feel recognized and acknowledged",
      "I somewhat feel recognized and acknowledged"]),
    ("Do you feel there is potential for growth at Homes First?", "Growth Opportunities",
     ["Yes, I do feel there is potential to grow"])
]
display_cross_analyses("Which racial or ethnic identity/identities best reflect you. (Select all that apply.)", race_outcomes)

st.markdown("---")

# --- Cross Analysis by Disability ---
st.subheader("By Disability Status")
disability_outcomes = [
    ("How fulfilling and rewarding do you find your work?", "Job Fulfillment",
     ["I find the work I do extremely fulfilling and rewarding",
      "I find the work I do fulfilling and rewarding in some parts and not so much in others"]),
    ("How likely are you to recommend Homes First as a good place to work?", "Recommendation", [8,9,10]),
    ("Do you feel you get acknowledged and recognized for your contribution  at work?", "Recognition",
     ["Yes, I do feel recognized and acknowledged",
      "I somewhat feel recognized and acknowledged"]),
    ("Do you feel there is potential for growth at Homes First?", "Growth Opportunities",
     ["Yes, I do feel there is potential to grow"])
]
display_cross_analyses("Do you identify as an individual living with a disability/disabilities and if so, what type of disability/disabilities do you have? (Select all that apply.)", disability_outcomes)
