import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Page configuration
st.set_page_config(page_title="Survey Cross-Analysis", page_icon="📊", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main {padding: 0rem 1rem;}
    h1 {color: #2c3e50; padding-bottom: 10px;}
    h2 {color: #34495e; padding-top: 15px; padding-bottom: 10px;}
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel('Combined- Cross Analysis.xlsx')
    df = df.iloc[:, :7]  # Only the first 7 relevant columns
    df.columns = [
        'Role', 
        'Ethnicity', 
        'Disability', 
        'Work_Fulfillment', 
        'Recommendation_Score', 
        'Recognition', 
        'Growth_Potential'
    ]
    return df

df = load_data()

# Filter target roles
target_roles = [
    "Administrator",
    "Coordinator",
    "Prefer not to disclose/other",
    "Generalist",
    "Analyst",
    "Supervisor (Shelters/Housing)",
    "Director/Assistant Director/Manager/Assistant Manager (HR/Finance/Property/Fundraising/Development)",
    "Director/Assistant Director/Manager/Assistant Manager/Site Manager (Shelters/Housing)",
    "Supervisor (HR/Finance/Property/Fundraising/Development)",
    "CSW - Shelters",
    "Non-24 Hour Program (including ICM, follow-up supports and PSW)",
    "Relief",
    "ICM - Shelters (includes ICM, HHW, Community Engagement, ICM Health Standards, etc.)",
    "Other (Smaller departments/teams not listed seperately in an effort to maintain confidentiality)"
]

df = df[df['Role'].isin(target_roles)]

# Sidebar filters
st.sidebar.header("🔍 Filter Data")
roles = ['All'] + sorted(df['Role'].unique().tolist())
selected_role = st.sidebar.selectbox("Role/Department", roles)

ethnicities = ['All'] + sorted(df['Ethnicity'].unique().tolist())
selected_ethnicity = st.sidebar.selectbox("Ethnicity", ethnicities)

# Apply filters
filtered_df = df.copy()
if selected_role != 'All':
    filtered_df = filtered_df[filtered_df['Role'] == selected_role]
if selected_ethnicity != 'All':
    filtered_df = filtered_df[filtered_df['Ethnicity'].str.contains(selected_ethnicity)]

total = len(filtered_df)

# Header
st.title("📊 Employee Survey Cross-Analysis Dashboard")
st.markdown("### Comparing Employee Groups Across Survey Questions")

# Metric Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Responses", total)

with col2:
    avg_score = filtered_df['Recommendation_Score'].mean()
    st.metric("Avg Recommendation", f"{avg_score:.1f}/10")

with col3:
    promoters = len(filtered_df[filtered_df['Recommendation_Score'] >= 9])
    detractors = len(filtered_df[filtered_df['Recommendation_Score'] <= 6])
    nps = ((promoters - detractors) / total * 100) if total > 0 else 0
    st.metric("NPS Score", f"{nps:.0f}")

with col4:
    fulfilled = len(filtered_df[filtered_df['Work_Fulfillment'].str.contains('extremely', case=False, na=False)])
    pct = (fulfilled / total * 100) if total > 0 else 0
    st.metric("Highly Fulfilled", f"{pct:.0f}%")

st.markdown("---")

# === SECTION: Recognition & Growth Sentiment Across Groups ===
st.markdown("## 🌟 Recognition & Growth Sentiment Across Groups")
st.markdown("<div style='margin-bottom:15px;'>Sentiment distribution by Role (%)</div>", unsafe_allow_html=True)

# Map Recognition & Growth
recog_map = {
    'Yes, I do feel recognized and acknowledged': 'Yes',
    'I somewhat feel recognized and acknowledged': 'Somewhat',
    "I do find myself being recognized and acknowledged, but it's rare given the contributions I make": 'Rare',
    "I don't feel recognized and acknowledged and would prefer staff successes to be highlighted more frequently": 'No (Want More)',
    "I don't feel recognized and acknowledged but I prefer it that way": 'No (Prefer)'
}

growth_map = {
    'Yes, I do feel there is potential to grow and I hope to advance my career with Homes First': 'Yes',
    'There is some potential to grow and I hope to advance my career with Homes First': 'Some',
    'Potential to grow seems limited at Homes First and I will likely need to advance my career with another organization': 'Limited',
    'There is very little potential to grow although I would like to advance my career with Homes First': 'Very Limited',
    'I am not interested in career growth and prefer to remain in my current role': 'Not Interested'
}

filtered_df['Recognition_Short'] = filtered_df['Recognition'].map(recog_map)
filtered_df['Growth_Short'] = filtered_df['Growth_Potential'].map(growth_map)

top_roles = filtered_df['Role'].value_counts().index

# Crosstabs
recog_cross = pd.crosstab(
    filtered_df['Role'], filtered_df['Recognition_Short'], normalize='index'
) * 100
growth_cross = pd.crosstab(
    filtered_df['Role'], filtered_df['Growth_Short'], normalize='index'
) * 100

# Function for dynamic font color based on background
def font_color(val):
    if val > 50:
        return 'white'
    else:
        return 'black'

# Recognition Heatmap
fig_recog = go.Figure(go.Heatmap(
    z=recog_cross.values,
    x=recog_cross.columns,
    y=[r[:30] for r in recog_cross.index],
    colorscale=[[0, '#d73027'], [0.5, '#fee08b'], [1, '#1a9850']],
    text=np.round(recog_cross.values, 0),
    texttemplate="%{text}%",
    textfont=dict(color=[font_color(v) for row in recog_cross.values for v in row]),
    hovertemplate='<b>%{y}</b><br>%{x}: %{z:.1f}%<extra></extra>'
))
fig_recog.update_layout(
    title="Recognition Sentiment by Role (%)",
    xaxis_title="Recognition Level",
    yaxis_title="",
    height=500,
    margin=dict(t=100, b=50)
)

# Growth Heatmap
fig_growth = go.Figure(go.Heatmap(
    z=growth_cross.values,
    x=growth_cross.columns,
    y=[r[:30] for r in growth_cross.index],
    colorscale=[[0, '#d73027'], [0.5, '#fee08b'], [1, '#1a9850']],
    text=np.round(growth_cross.values, 0),
    texttemplate="%{text}%",
    textfont=dict(color=[font_color(v) for row in growth_cross.values for v in row]),
    hovertemplate='<b>%{y}</b><br>%{x}: %{z:.1f}%<extra></extra>'
))
fig_growth.update_layout(
    title="Growth Potential by Role (%)",
    xaxis_title="Growth Perception",
    yaxis_title="",
    height=500,
    margin=dict(t=100, b=50)
)

col1, col2 = st.columns(2)
col1.plotly_chart(fig_recog, use_container_width=True)
col2.plotly_chart(fig_growth, use_container_width=True)
