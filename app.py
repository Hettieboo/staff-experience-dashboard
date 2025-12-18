import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- Page Config ---
st.set_page_config(page_title="Survey Cross-Analysis", page_icon="📊", layout="wide")

# --- Load Data ---
@st.cache_data
def load_data():
    # Use relative path to Excel file in repo
    df = pd.read_excel("Combined- Cross Analysis.xlsx")
    df.columns = [
        'Role', 'Ethnicity', 'Disability', 'Work_Fulfillment',
        'Recommendation_Score', 'Recognition', 'Growth_Potential'
    ]
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
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Data")
roles = ['All'] + sorted(df['Role'].unique().tolist())
selected_role = st.sidebar.selectbox("Role/Department", roles)

# Extract all ethnicities (explode multi-select)
ethnicities = ['All'] + sorted(set(sum(df['Ethnicity'].dropna().str.split(','), [])))
ethnicities = [e.strip() for e in ethnicities]
selected_ethnicity = st.sidebar.selectbox("Ethnicity", ethnicities)

# --- Apply Filters ---
filtered_df = df.copy()
if selected_role != 'All':
    filtered_df = filtered_df[filtered_df['Role'] == selected_role]
if selected_ethnicity != 'All':
    filtered_df = filtered_df[filtered_df['Ethnicity'].str.contains(selected_ethnicity, na=False)]

total = len(filtered_df)

# --- Map Recognition & Growth ---
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

filtered_df['Recognition_Short'] = filtered_df['Recognition'].map(recog_map).fillna('No Response')
filtered_df['Growth_Short'] = filtered_df['Growth_Potential'].map(growth_map).fillna('No Response')

# --- Metrics ---
st.title("📊 Employee Survey Cross-Analysis Dashboard")
st.markdown("### Comparing Employee Groups Across Survey Questions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Responses", total)

with col2:
    avg_score = filtered_df['Recommendation_Score'].mean() if total > 0 else 0
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

# --- Crosstabs ---
recog_cross_role = pd.crosstab(filtered_df['Role'], filtered_df['Recognition_Short'], normalize='index').fillna(0) * 100
growth_cross_role = pd.crosstab(filtered_df['Role'], filtered_df['Growth_Short'], normalize='index').fillna(0) * 100

# --- Truncate role names ---
truncated_roles = [r if len(r) <= 25 else r[:22] + "..." for r in recog_cross_role.index]

# --- Font color matrix ---
def font_color_matrix(z):
    return [['white' if v > 50 else 'black' for v in row] for row in z]

# --- Recognition Heatmap ---
fig_recog = go.Figure(go.Heatmap(
    z=recog_cross_role.values,
    x=recog_cross_role.columns,
    y=truncated_roles,
    colorscale=[[0, '#d73027'], [0.5, '#fee08b'], [1, '#1a9850']],
    text=np.round(recog_cross_role.values, 0),
    texttemplate="%{text}%",
    textfont=dict(color=font_color_matrix(recog_cross_role.values)),
    hovertemplate='<b>%{y}</b><br>%{x}: %{z:.1f}%<extra></extra>'
))
fig_recog.update_layout(title="Recognition Sentiment by Role (%)", xaxis_title="Recognition Level", yaxis_title="Role", height=500)

# --- Growth Heatmap ---
fig_growth = go.Figure(go.Heatmap(
    z=growth_cross_role.values,
    x=growth_cross_role.columns,
    y=truncated_roles,
    colorscale=[[0, '#d73027'], [0.5, '#fee08b'], [1, '#1a9850']],
    text=np.round(growth_cross_role.values, 0),
    texttemplate="%{text}%",
    textfont=dict(color=font_color_matrix(growth_cross_role.values)),
    hovertemplate='<b>%{y}</b><br>%{x}: %{z:.1f}%<extra></extra>'
))
fig_growth.update_layout(title="Growth Potential by Role (%)", xaxis_title="Growth Perception", yaxis_title="Role", height=500)

# --- Display Heatmaps ---
st.markdown("## 🌟 Recognition & Growth Sentiment Across Roles")
col1, col2 = st.columns(2)
col1.plotly_chart(fig_recog, use_container_width=True)
col2.plotly_chart(fig_growth, use_container_width=True)
