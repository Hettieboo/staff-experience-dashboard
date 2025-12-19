import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Page config
st.set_page_config(page_title="Homes First Survey Dashboard", layout="wide")

# Custom CSS - smaller KPI cards
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0.8rem 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.85rem;
        opacity: 0.9;
    }
    .insight-card {
        background: #f0f7ff;
        border-left: 4px solid #667eea;
        padding: 0.9rem;
        margin: 0.4rem 0;
        border-radius: 5px;
        font-size: 0.9rem;
    }
    .insight-positive {
        background: #f0fff4;
        border-left: 4px solid #48bb78;
    }
    .insight-negative {
        background: #fff5f5;
        border-left: 4px solid #f56565;
    }
    .insight-neutral {
        background: #fffaf0;
        border-left: 4px solid #ed8936;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel('Combined- Cross Analysis.xlsx')
    df.columns = ['Role', 'Ethnicity', 'Disability', 'Work_Fulfillment',
                  'Recommendation_Score', 'Recognition', 'Growth_Potential']
    return df

df = load_data()

# Title
st.markdown('<div class="main-title">Homes First Employee Survey Dashboard</div>', unsafe_allow_html=True)

# Sidebar filters
st.sidebar.header("Filters")
roles = ['All'] + sorted(df['Role'].dropna().unique().tolist())
role_filter = st.sidebar.selectbox("Role", roles)
ethnicities = ['All'] + sorted(df['Ethnicity'].dropna().unique().tolist())
ethnicity_filter = st.sidebar.selectbox("Ethnicity", ethnicities)
disabilities = ['All'] + sorted(df['Disability'].dropna().unique().tolist())
disability_filter = st.sidebar.selectbox("Disability", disabilities)

# Apply filters
filtered_df = df.copy()
if role_filter != 'All': filtered_df = filtered_df[filtered_df['Role'] == role_filter]
if ethnicity_filter != 'All': filtered_df = filtered_df[filtered_df['Ethnicity'] == ethnicity_filter]
if disability_filter != 'All': filtered_df = filtered_df[filtered_df['Disability'] == disability_filter]

# Helper functions
def get_score_band(score):
    if pd.isna(score): return np.nan
    if score <= 3: return '0–3'
    elif score <= 6: return '4–6'
    elif score <= 8: return '7–8'
    else: return '9–10'

def categorize_disability(disability_text):
    if isinstance(disability_text, float) and np.isnan(disability_text): return 'Unknown'
    text = str(disability_text).lower()
    if 'do not identify' in text: return 'No Disability'
    elif 'prefer not to specify' in text: return 'Prefer Not to Specify'
    else: return 'With Disability'

def shorten_role(role):
    mapping = {
        'Director/Assistant Director/Manager/Assistant Manager (HR/Finance/Property/Fundraising/Development)': 'Director/Manager (HR/Finance/Dev)',
        'Director/Assistant Director/Manager/Assistant Manager/Site Manager (Shelters/Housing)': 'Director/Manager (Shelters)',
        'Supervisor (Shelters/Housing)': 'Supervisor (Shelters)',
        'Supervisor (HR/Finance/Property/Fundraising/Development)': 'Supervisor (HR/Finance/Dev)',
        'ICM - Shelters (includes ICM, HHW, Community Engagement, ICM Health Standards, etc.)': 'ICM - Shelters',
        'Non-24 Hour Program (including ICM, follow-up supports and PSW)': 'Non-24 Hour Program',
        'Other (Smaller departments/teams not listed seperately in an effort to maintain confidentiality)': 'Other',
        'Prefer not to disclose/Other': 'Prefer not to disclose',
    }
    return mapping.get(role, role)

def shorten_text(text, max_length=60):
    if not isinstance(text, str): return str(text)
    return text if len(text) <= max_length else text[:max_length-3] + '...'

filtered_df['Score_Band'] = filtered_df['Recommendation_Score'].apply(get_score_band)
df['Disability_Category'] = df['Disability'].apply(categorize_disability)
filtered_df['Disability_Category'] = filtered_df['Disability'].apply(categorize_disability)

# ============= 1. KPIs (SMALLER CARDS) =============
st.markdown("## 📌 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{len(filtered_df)}</div>
        <div class="metric-label">Total Responses</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    avg_score_f = filtered_df['Recommendation_Score'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{avg_score_f:.1f if not np.isnan(avg_score_f) else 0:.1f}</div>
        <div class="metric-label">Avg Recommendation</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    low_scores_f = len(filtered_df[filtered_df['Recommendation_Score'] <= 4])
    high_scores_f = len(filtered_df[filtered_df['Recommendation_Score'] >= 8])
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{low_scores_f}/{high_scores_f}</div>
        <div class="metric-label">Low/High Scores</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    extremely_fulfilling_f = len(filtered_df[filtered_df['Work_Fulfillment'].str.contains('extremely', case=False, na=False)])
    pct_extremely_f = (extremely_fulfilling_f / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{pct_extremely_f:.0f}%</div>
        <div class="metric-label">"Extremely" Fulfilling</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============= 2. KEY INSIGHTS (BELOW KPIs) =============
st.markdown("## 🔍 Key Insights")
overall_avg = df['Recommendation_Score'].mean()

disability_scores = df.groupby('Disability_Category')['Recommendation_Score'].agg(['mean', 'count']).round(2)
disability_scores = disability_scores[disability_scores['count'] >= 5]

role_scores = df.groupby('Role')['Recommendation_Score'].agg(['mean', 'count']).round(2)
role_scores = role_scores[role_scores['count'] >= 5]
lowest_role = role_scores['mean'].idxmin() if len(role_scores) > 0 else None
highest_role = role_scores['mean'].idxmax() if len(role_scores) > 0 else None

extremely_fulfilling = df[df['Work_Fulfillment'].str.contains('extremely', case=False, na=False)]
avg_score_extremely = extremely_fulfilling['Recommendation_Score'].mean()
not_extremely = df[~df['Work_Fulfillment'].str.contains('extremely', case=False, na=False)]
avg_score_not_extremely = not_extremely['Recommendation_Score'].mean()

col_ins1, col_ins2 = st.columns(2)
with col_ins1:
    st.markdown("### 📊 Overall Patterns")
    diff_fulfillment = avg_score_extremely - avg_score_not_extremely
    if not np.isnan(diff_fulfillment) and diff_fulfillment > 2:
        st.markdown(f'<div class="insight-card insight-positive"><strong>✅ Fulfillment Link:</strong> "Extremely fulfilling" scores {diff_fulfillment:.1f}pts higher</div>', unsafe_allow_html=True)
    
    if lowest_role: st.markdown(f'<div class="insight-card insight-negative"><strong>⚠️ Lowest Role:</strong> {shorten_role(lowest_role)} ({role_scores.loc[lowest_role, "mean"]:.1f})</div>', unsafe_allow_html=True)
    if highest_role: st.markdown(f'<div class="insight-card insight-positive"><strong>✅ Highest Role:</strong> {shorten_role(highest_role)} ({role_scores.loc[highest_role, "mean"]:.1f})</div>', unsafe_allow_html=True)

with col_ins2:
    st.markdown("### 👥 Demographics")
    if {'With Disability', 'No Disability'} <= set(disability_scores.index):
        diff_dis = disability_scores.loc['No Disability', 'mean'] - disability_scores.loc['With Disability', 'mean']
        if abs(diff_dis) > 1:
            st.markdown(f'<div class="insight-card insight-negative"><strong>⚠️ Disability Gap:</strong> {abs(diff_dis):.1f}pts difference</div>', unsafe_allow_html=True)

st.markdown("---")

# ============= 3. STACKED BAR HELPER =============
def create_stacked_bar(df_in, question_col, title, top_n=8):
    sub = df_in[['Role', question_col]].dropna()
    if sub.empty: return st.info(f"No data for {title}")
    
    top_roles = sub['Role'].value_counts().head(top_n).index
    sub = sub[sub['Role'].isin(top_roles)].copy()
    sub['Role_Short'] = sub['Role'].apply(shorten_role)
    
    tab = pd.crosstab(sub['Role_Short'], sub[question_col], normalize='index') * 100
    long_df = tab.reset_index().melt(id_vars='Role_Short', var_name='Answer', value_name='Percent')
    long_df['Answer_Short'] = long_df['Answer'].apply(lambda x: shorten_text(str(x), 40))
    
    height = max(450, 50 * len(top_roles))
    fig = px.bar(long_df, x='Percent', y='Role_Short', color='Answer_Short', orientation='h',
                barmode='stack', title=title, height=height)
    fig.update_layout(xaxis_tickformat='.0f', legend=dict(orientation="h", y=1.02, x=0.5, font_size=10))
    st.plotly_chart(fig, use_container_width=True)

# ============= 4. QUESTION BREAKDOWNS =============
st.markdown("## 📊 Question Breakdowns by Role")

# Recommendation
st.subheader("Recommendation Score (0-10)")
col1, col2 = st.columns(2)
with col1:
    rec_counts = filtered_df['Recommendation_Score'].dropna().astype(int).value_counts().sort_index().reset_index()
    rec_counts.columns = ['Score', 'Count']
    all_scores = pd.DataFrame({'Score': range(11)})
    rec_counts = all_scores.merge(rec_counts, on='Score', how='left').fillna(0)['Count'].astype(int)
    fig_rec = px.bar(x=rec_counts.values, y=all_scores['Score'], orientation='h', 
                    title='Score Distribution', color=rec_counts.values, color_continuous_scale='Blues')
    st.plotly_chart(fig_rec, use_container_width=True)

with col2:
    if 'Score_Band' in filtered_df.columns:
        band_counts = filtered_df['Score_Band'].value_counts().reindex(['0–3','4–6','7–8','9–10'], fill_value=0)
        fig_donut = px.pie(values=band_counts.values, names=band_counts.index, hole=0.4, 
                          title='Score Bands', color_discrete_sequence=['#ef5350','#ffa726','#66bb6a','#42a5f5'])
        st.plotly_chart(fig_donut, use_container_width=True)

create_stacked_bar(filtered_df, 'Score_Band', 'Recommendation Bands by Role', top_n=8)

# Other questions
for q, title in [('Work_Fulfillment', 'Work Fulfillment'), ('Recognition', 'Recognition'), ('Growth_Potential', 'Growth Potential')]:
    st.markdown(f"---")
    st.subheader(f"{title} by Role")
    create_stacked_bar(filtered_df, q, f'{title} Distribution by Role (Top 8)', top_n=8)

# ============= 5. CONTEXT CHARTS (FROM OLDER VERSION) =============
st.markdown("## 👥 Context: Who Responded?")
tab1, tab2 = st.tabs(["🌍 Ethnicity", "♿ Disability"])

with tab1:
    eth_counts = filtered_df['Ethnicity'].dropna().value_counts().head(15)
    if len(eth_counts) > 0:
        fig_eth = px.bar(eth_counts.reset_index(), y='index', x='Ethnicity', orientation='h',
                        title=f"Top Ethnicities (n={len(eth_counts)})", height=max(450, 40*len(eth_counts)))
        st.plotly_chart(fig_eth, use_container_width=True)
        col1, col2 = st.columns(2)
        col1.metric("Unique Ethnicities", len(filtered_df['Ethnicity'].dropna().unique()))
        col2.metric("Most Common", eth_counts.index[0])

with tab2:
    dis_counts = filtered_df['Disability'].dropna().value_counts().head(15)
    if len(dis_counts) > 0:
        fig_dis = px.bar(dis_counts.reset_index(), y='index', x='Disability', orientation='h',
                        title=f"Top Disability Categories (n={len(dis_counts)})", height=max(450, 40*len(dis_counts)))
        st.plotly_chart(fig_dis, use_container_width=True)
    no_dis = len(filtered_df[filtered_df['Disability'].str.contains('do not identify', case=False, na=False)])
    col1, col2 = st.columns(2)
    col1.metric("No Disability", no_dis)
    col2.metric("With Disability", len(filtered_df) - no_dis)

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666; padding: 1rem;'><p>📊 Homes First Survey Dashboard | Filters apply to all charts</p></div>", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("**Complete Dashboard v2.0**")
