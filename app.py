# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================
# Load Data
# ==========================
@st.cache_data
def load_data():
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
col1, col2, col3, col4 = st.columns(4)

total_responses = len(df)
high_fulfillment = df['High Fulfillment'].sum() if 'High Fulfillment' in df.columns else 0
would_recommend = df['Would Recommend'].sum() if 'Would Recommend' in df.columns else 0
sees_growth = df['Sees Growth'].sum() if 'Sees Growth' in df.columns else 0

col1.metric("Responses", total_responses)
col2.metric("High Fulfillment", f"{high_fulfillment / total_responses * 100:.0f}%" if total_responses else "0%")
col3.metric("Would Recommend", f"{would_recommend / total_responses * 100:.0f}%" if total_responses else "0%")
col4.metric("Sees Growth", f"{sees_growth / total_responses * 100:.0f}%" if total_responses else "0%")

st.markdown("---")

# ==========================
# Cross Analysis Categories
# ==========================
categories = [
    {"name": "By Role Group", "column": "Role Group"},
    {"name": "By Race/Ethnicity", "column": "Racial or Ethnic Identity"},
    {"name": "By Disability", "column": "Disability Status"}
]

# ==========================
# Cross Analysis Tabs
# ==========================
tabs = st.tabs([cat["name"] for cat in categories])

for tab, cat in zip(tabs, categories):
    with tab:
        st.markdown(
            f"<div style='background-color:#e8f0fe;padding:8px;border-radius:4px;font-weight:bold;margin-bottom:10px;'>{cat['name']}</div>",
            unsafe_allow_html=True
        )

        chart_cols = st.columns(2)

        # Job Fulfillment Chart
        if 'Job Fulfillment' in df.columns:
            fulfill_data = df.groupby(cat["column"])['Job Fulfillment'].value_counts().unstack().fillna(0)
            fig_fulfill = px.bar(
                fulfill_data,
                barmode='stack',
                title="Job Fulfillment",
                labels={cat["column"]: cat["name"], 'value': 'Count', 'variable':'Response'}
            )
            fig_fulfill.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
            chart_cols[0].plotly_chart(fig_fulfill, use_container_width=True)

        # Recommendation Chart
        if 'Recommendation' in df.columns:
            recommend_data = df.groupby(cat["column"])['Recommendation'].value_counts().unstack().fillna(0)
            fig_recommend = px.bar(
                recommend_data,
                barmode='stack',
                title="Recommendation",
                labels={cat["column"]: cat["name"], 'value': 'Count', 'variable':'Response'}
            )
            fig_recommend.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
            chart_cols[1].plotly_chart(fig_recommend, use_container_width=True)

        # Recognition Chart
        if 'Recognition' in df.columns:
            recognition_data = df.groupby(cat["column"])['Recognition'].value_counts().unstack().fillna(0)
            fig_recognition = px.bar(
                recognition_data,
                barmode='stack',
                title="Recognition",
                labels={cat["column"]: cat["name"], 'value': 'Count', 'variable':'Response'}
            )
            fig_recognition.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_recognition, use_container_width=True)

        # Growth Opportunities Chart
        if 'Growth Opportunities' in df.columns:
            growth_data = df.groupby(cat["column"])['Growth Opportunities'].value_counts().unstack().fillna(0)
            fig_growth = px.bar(
                growth_data,
                barmode='stack',
                title="Growth Opportunities",
                labels={cat["column"]: cat["name"], 'value': 'Count', 'variable':'Response'}
            )
            fig_growth.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_growth, use_container_width=True)

        st.markdown("---")

# ==========================
# Footer
# ==========================
st.markdown(
    "<div style='text-align:center; color:gray; padding:10px;'>Staff Experience Dashboard &copy; 2025</div>",
    unsafe_allow_html=True
)
