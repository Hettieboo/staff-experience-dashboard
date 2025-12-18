import streamlit as st
import pandas as pd
import plotly.express as px

# Load Data
@st.cache_data
def load_data():
    df = pd.read_excel("Combined- Cross Analysis.xlsx")
    return df

df = load_data()

# Page title
st.title("Staff Experience & Job Fulfillment")
st.markdown("Cross-analysis of organizational and demographic factors influencing staff experience.")

# Key indicators
st.subheader("Key Indicators")
col1, col2, col3 = st.columns(3)
with col1:
    high_fulfillment = df['How fulfilling and rewarding do you find your work?'].value_counts().get("I find the work I do extremely fulfilling and rewarding", 0)
    st.metric("High Fulfillment", f"{high_fulfillment} / {len(df)}")
with col2:
    recommend = df['How likely are you to recommend Homes First as a good place to work?'].mean()
    st.metric("Would Recommend", f"{recommend:.0f}%")
with col3:
    growth = df['Do you feel there is potential for growth at Homes First?'].value_counts().get("Yes, I do feel there is potential to grow and I hope to advance my career with Homes First", 0)
    st.metric("Sees Growth", f"{growth / len(df) * 100:.0f}%")

# Cross Analysis using tabs
tabs = st.tabs([
    "By Role Group",
    "By Race/Ethnicity",
    "By Disability"
])

categories = [
    ("Select your role/department", "By Role Group"),
    ("Which racial or ethnic identity/identities best reflect you. (Select all that apply.)", "By Race/Ethnicity"),
    ("Do you identify as an individual living with a disability/disabilities and if so, what type of disability/disabilities do you have? (Select all that apply.)", "By Disability")
]

for tab, (question_col, tab_name) in zip(tabs, categories):
    with tab:
        st.markdown(f"### {tab_name}")
        st.markdown(f"<div style='background-color:#f0f0f0;padding:6px;border-radius:4px;font-weight:bold;'>{question_col}</div>", unsafe_allow_html=True)
        
        # Example chart: Job Fulfillment distribution
        fig_fulfill = px.bar(
            df.groupby(question_col)['How fulfilling and rewarding do you find your work?'].value_counts().unstack().fillna(0),
            barmode='stack',
            title="Job Fulfillment"
        )
        fig_fulfill.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_fulfill, use_container_width=True)
        
        # Example chart: Recommendation
        fig_recommend = px.bar(
            df.groupby(question_col)['How likely are you to recommend Homes First as a good place to work?'].mean().reset_index(),
            x=question_col, y='How likely are you to recommend Homes First as a good place to work?',
            title="Recommendation"
        )
        fig_recommend.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_recommend, use_container_width=True)
