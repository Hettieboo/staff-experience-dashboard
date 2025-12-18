import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page configuration ---
st.set_page_config(
    page_title="Staff Experience & Job Fulfillment",
    layout="wide"
)

# --- Load data ---
@st.cache_data
def load_data():
    df = pd.read_excel("Combined- Cross Analysis.xlsx")  # Update with your exact file name
    return df

df = load_data()

# --- Key indicators ---
total_responses = df.shape[0]
high_fulfillment = (df["How fulfilling and rewarding do you find your work?"] >= 8).mean() * 100
would_recommend = (df["How likely are you to recommend Homes First as a good place to work?"] >= 8).mean() * 100
sees_growth = (df["Do you feel there is potential for growth at Homes First?"].str.contains("Yes", na=False)).mean() * 100

st.title("Staff Experience & Job Fulfillment")
st.markdown("Cross-analysis of organizational and demographic factors influencing staff experience.")

# Display key indicators
st.markdown("### Key Indicators")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Responses", total_responses)
col2.metric("High Fulfillment (%)", f"{high_fulfillment:.0f}%")
col3.metric("Would Recommend (%)", f"{would_recommend:.0f}%")
col4.metric("Sees Growth (%)", f"{sees_growth:.0f}%")

# --- Utility function to create charts ---
def plot_bar(data, category_col, value_col, title):
    fig = px.bar(
        data_frame=data,
        x=category_col,
        y=value_col,
        color=value_col,
        color_continuous_scale='Viridis',
        text_auto=True
    )
    fig.update_layout(
        title=title,
        xaxis_title=category_col,
        yaxis_title=value_col,
        coloraxis_showscale=False,
        height=400
    )
    return fig

# --- Questions and cross-analysis ---
questions = {
    "Job Fulfillment": "How fulfilling and rewarding do you find your work?",
    "Recommendation": "How likely are you to recommend Homes First as a good place to work?",
    "Recognition": "Do you feel you get acknowledged and recognized for your contribution  at work?",
    "Growth Opportunities": "Do you feel there is potential for growth at Homes First?",
}

categories = [
    ("Role/Department", "Select the role/department that best describes your current position at Homes First."),
    ("Racial/Ethnic Identity", "Which racial or ethnic identity/identities best reflect you. (Select all that apply.)"),
    ("Disability", "Do you identify as an individual living with a disability/disabilities and if so, what type of disability/disabilities do you have? (Select all that apply.)")
]

for cat_name, cat_col in categories:
    st.markdown(f"### Cross Analysis by {cat_name}")
    for q_name, q_col in questions.items():
        st.markdown(f"#### {q_name}")
        # Aggregate data
        if df[q_col].dtype == "object":
            summary = df.groupby(cat_col)[q_col].value_counts(normalize=True).rename("Percentage").reset_index()
            summary["Percentage"] *= 100
        else:
            summary = df.groupby(cat_col)[q_col].mean().reset_index()
        # Plot chart
        fig = plot_bar(summary, cat_col, "Percentage" if "Percentage" in summary.columns else q_col, f"{q_name} by {cat_name}")
        st.plotly_chart(fig, use_container_width=True)
