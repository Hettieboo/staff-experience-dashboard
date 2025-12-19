import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Homes First Survey Dashboard", layout="wide")

# ================= CUSTOM CSS =================
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 5px 0;
    }
    .metric-label {
        font-size: 0.85rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# ================= LOAD DATA =================
@st.cache_data
def load_data():
    df = pd.read_excel('Combined- Cross Analysis.xlsx')
    df.columns = ['Role', 'Ethnicity', 'Disability', 'Work_Fulfillment', 
                  'Recommendation_Score', 'Recognition', 'Growth_Potential']
    return df

df = load_data()

# ================= TITLE =================
st.markdown('<div class="main-title">Homes First Employee Survey Dashboard</div>', unsafe_allow_html=True)

# ================= SIDEBAR FILTERS =================
st.sidebar.header("Filters")
roles = ['All'] + sorted(df['Role'].unique().tolist())
role_filter = st.sidebar.selectbox("Role", roles)

# Added filters
ethnicities = ['All'] + sorted(df['Ethnicity'].unique().tolist())
ethnicity_filter = st.sidebar.selectbox("Ethnicity", ethnicities)
disabilities = ['All'] + sorted(df['Disability'].unique().tolist())
disability_filter = st.sidebar.selectbox("Disability", disabilities)

filtered_df = df.copy()
if role_filter != 'All':
    filtered_df = filtered_df[filtered_df['Role'] == role_filter]
if ethnicity_filter != 'All':
    filtered_df = filtered_df[filtered_df['Ethnicity'] == ethnicity_filter]
if disability_filter != 'All':
    filtered_df = filtered_df[filtered_df['Disability'] == disability_filter]

# ================= HELPER FUNCTIONS =================
def get_score_band(score):
    if score <= 3: return '0-3'
    elif score <= 6: return '4-6'
    elif score <= 8: return '7-8'
    else: return '9-10'

def categorize_disability(disability_text):
    if 'do not identify' in disability_text.lower():
        return 'No Disability'
    elif 'prefer not to specify' in disability_text.lower():
        return 'Prefer Not to Specify'
    else:
        return 'With Disability'

def shorten_role(role):
    role_mapping = {
        'Director/Assistant Director/Manager/Assistant Manager (HR/Finance/Property/Fundraising/Development)': 'Director/Manager (HR/Finance/Dev)',
        'Director/Assistant Director/Manager/Assistant Manager/Site Manager (Shelters/Housing)': 'Director/Manager (Shelters)',
        'Supervisor (Shelters/Housing)': 'Supervisor (Shelters)',
        'Supervisor (HR/Finance/Property/Fundraising/Development)': 'Supervisor (HR/Finance/Dev)',
        'ICM - Shelters (includes ICM, HHW, Community Engagement, ICM Health Standards, etc.)': 'ICM - Shelters',
        'Non-24 Hour Program (including ICM, follow-up supports and PSW)': 'Non-24 Hour Program',
        'Other (Smaller departments/teams not listed seperately in an effort to maintain confidentiality)': 'Other',
        'Prefer not to disclose/Other': 'Prefer not to disclose',
        'CSW - Shelters': 'CSW - Shelters',
        'Relief': 'Relief'
    }
    return role_mapping.get(role, role)

def shorten_ethnicity(eth):
    if 'South Asian' in eth:
        return 'South Asian'
    elif 'Black (including East African' in eth:
        return 'Black (African)'
    elif 'Black (including Caribbean' in eth:
        return 'Black (Caribbean/Am)'
    elif 'White (including' in eth:
        return 'White'
    elif 'Middle Eastern' in eth:
        return 'Middle Eastern'
    elif len(eth) > 25:
        return eth[:22] + '...'
    return eth

df['Disability_Category'] = df['Disability'].apply(categorize_disability)
filtered_df['Disability_Category'] = filtered_df['Disability'].apply(categorize_disability)
filtered_df['Score_Band'] = filtered_df['Recommendation_Score'].apply(get_score_band)

# ================= KPI CARDS =================
st.markdown("## 📊 Key Performance Indicators (KPIs)")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{len(filtered_df)}</div>
        <div class="metric-label">Total Responses</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    avg_score = filtered_df['Recommendation_Score'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{avg_score:.1f}/10</div>
        <div class="metric-label">Avg Score</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    low_scores = len(filtered_df[filtered_df['Recommendation_Score'] <= 4])
    high_scores = len(filtered_df[filtered_df['Recommendation_Score'] >= 8])
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{low_scores}/{high_scores}</div>
        <div class="metric-label">Low/High Scores</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    extremely_fulfilling = len(filtered_df[filtered_df['Work_Fulfillment'].str.contains('extremely', case=False, na=False)])
    pct_extremely = (extremely_fulfilling / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{pct_extremely:.0f}%</div>
        <div class="metric-label">Highly Fulfilled</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    unique_ethnicities = filtered_df['Ethnicity'].nunique()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{unique_ethnicities}</div>
        <div class="metric-label">Ethnic Groups</div>
    </div>
    """, unsafe_allow_html=True)

with col6:
    with_disability = len(filtered_df[~filtered_df['Disability'].str.contains('do not identify', case=False, na=False)])
    pct_disability = (with_disability / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{pct_disability:.0f}%</div>
        <div class="metric-label">With Disability</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ================= CROSS-ANALYSIS TABS =================
st.markdown("## 📈 Cross-Analysis: Demographics vs. Employee Sentiment")
tab1, tab2, tab3, tab4 = st.tabs(["🎯 By Role", "🌍 By Ethnicity", "♿ By Disability", "🔥 Heatmaps"])

df_insights = filtered_df.copy()
df_insights['Role_Short'] = df_insights['Role'].apply(shorten_role)

# ======= TAB 1: BY ROLE =======
with tab1:
    st.markdown("### Analysis by Role/Department")
    
    top_roles = df['Role'].value_counts().head(8).index.tolist()
    df_cross = df[df['Role'].isin(top_roles)].copy()
    df_cross['Role_Short'] = df_cross['Role'].apply(shorten_role)
    
    # ... all your Role charts logic unchanged ...
    # (Work Fulfillment, Recognition, Growth Potential)

# ======= TAB 2: BY ETHNICITY =======
with tab2:
    st.markdown("### Analysis by Ethnicity")
    
    top_ethnicities = df['Ethnicity'].value_counts().head(8).index.tolist()
    df_eth = df[df['Ethnicity'].isin(top_ethnicities)].copy()
    df_eth['Ethnicity_Short'] = df_eth['Ethnicity'].apply(shorten_ethnicity)
    
    # ... all your Ethnicity charts logic unchanged ...

# ======= TAB 3: BY DISABILITY =======
with tab3:
    st.markdown("### Analysis by Disability Status")
    
    df_dis = df.copy()
    df_dis['Disability_Short'] = df_dis['Disability_Category']
    
    # ... all your Disability charts logic unchanged ...

# ======= TAB 4: HEATMAPS =======
with tab4:
    st.markdown("### Sentiment Heatmaps")
    
    # ... all your heatmap logic unchanged ...
