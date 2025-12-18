import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================
# Load Data
# ==========================
@st.cache_data
def load_data():
    # Replace with your actual Excel file path
    df = pd.read_excel("Combined- Cross Analysis.xlsx")
    return df

df = load_data()

# ==========================
# Page Configuration
# ==========================
st.set_page_config(page_title="Staff Experience Dashboard", layout="wide")
st.title("Staff Experience & Job Fulfillment")
st.markdown(
    "Cross-analysis of organizational and demographic factors influencing staff experience."
)

# ==========================
# Key Indicators
# ==========================
st.subheader("Key Indicators")
col1, col2, col3 = st.columns(3)

# Example calculations (update based on your survey responses column names)
high_fulfillment = df['How fulfilling and rewarding do you find your work?'].value_counts().get(
    "I find the work I do extremely fulfilling and rewarding", 0
)
recommend = df['How likely are you to recommend Homes First as a good place to work?'].mean()
growth = df['Do you feel there is potential for growth at Homes First?'].value_counts().get(
    "Yes, I do feel there is potential to grow and I hope to advance my career with Homes First", 0
)

with col1:
    st.metric("High Fulfillment", f"{high_fulfillment} / {len(df)}")
with col2:
    st.metric("Would Recommend", f"{recommend:.0f}%")
with col3:
    st.metric("Sees Growth", f"{growth / len(df) * 100:.0f}%")

st.markdown("---")

# ==========================
# Define Cross Analysis Categories
# ==========================
categories = [
    {
        "name": "By Role Group",
        "column": "Select your role/department"
    },
    {
        "name": "By Race/Ethnicity",
        "column": "Which racial or ethnic identity/identities best reflect you. (Select all that apply.)"
    },
    {
        "name": "By Disability",
        "column": "Do you identify as an individual living with a disability/disabilities and if so, what type of disability/disabilities do you have? (Select all that apply.)"
    }
]

# ==========================
# Cross Analysis Tabs
# ==========================
tabs = st.tabs([cat["name"] for cat in categories])

for tab, cat in zip(tabs, categories):
    with tab:
        st.markdown(
            f"<div style='background-color:#f0f0f0;padding:6px;border-radius:4px;font-weight:bold;'>{cat['column']}</div>",
            unsafe_allow_html=True
        )

        # Use columns to display multiple charts side by side
        chart_cols = st.columns(2)

        # ---- Job Fulfillment ----
        fulfill_data = df.groupby(cat["column"])['How fulfilling and rewarding do you find your work?'] \
                         .value_counts().unstack().fillna(0)
        fig_fulfill = px.bar(
            fulfill_data,
            barmode='stack',
            title="Job Fulfillment"
        )
        fig_fulfill.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
        chart_cols[0].plotly_chart(fig_fulfill, use_container_width=True)

        # ---- Recommendation ----
        recommend_data = df.groupby(cat["column"])['How likely are you to recommend Homes First as a good place to work?'] \
                           .mean().reset_index()
        fig_recommend = px.bar(
            recommend_data,
            x=cat["column"], y='How likely are you to recommend Homes First as a good place to work?',
            title="Recommendation",
            color='How likely are you to recommend Homes First as a good place to work?',
            color_continuous_scale='Blues'
        )
        fig_recommend.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
        chart_cols[1].plotly_chart(fig_recommend, use_container_width=True)

        # ---- Recognition ----
        recognition_data = df.groupby(cat["column"])['Do you feel recognized for your work?'].value_counts().unstack().fillna(0)
        fig_recognition = px.bar(
            recognition_data,
            barmode='stack',
            title="Recognition"
        )
        fig_recognition.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_recognition, use_container_width=True)

        # ---- Growth Opportunities ----
        growth_data = df.groupby(cat["column"])['Do you feel there is potential for growth at Homes First?'].value_counts().unstack().fillna(0)
        fig_growth = px.bar(
            growth_data,
            barmode='stack',
            title="Growth Opportunities"
        )
        fig_growth.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_growth, use_container_width=True)

        st.markdown("---")
