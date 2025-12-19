import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Page config
st.set_page_config(page_title="Homes First Survey Dashboard", layout="wide")

# Custom CSS  ─── reduced KPI size here
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
        padding: 0.8rem 1rem;              /* was 1.5rem → smaller */
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 0.5rem;             /* slightly reduced */
    }
    .metric-value {
        font-size: 1.6rem;                 /* was 2.5rem → smaller */
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.85rem;                /* was 1rem → smaller */
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
if role_filter != 'All':
    filtered_df = filtered_df[filtered_df['Role'] == role_filter]
if ethnicity_filter != 'All':
    filtered_df = filtered_df[filtered_df['Ethnicity'] == ethnicity_filter]
if disability_filter != 'All':
    filtered_df = filtered_df[filtered_df['Disability'] == disability_filter]

# Helper functions (same as before) ...
def get_score_band(score):
    if pd.isna(score):
        return np.nan
    if score <= 3:
        return '0–3'
    elif score <= 6:
        return '4–6'
    elif score <= 8:
        return '7–8'
    else:
        return '9–10'

filtered_df['Score_Band'] = filtered_df['Recommendation_Score'].apply(get_score_band)

def categorize_disability(disability_text):
    if isinstance(disability_text, float) and np.isnan(disability_text):
        return 'Unknown'
    text = str(disability_text).lower()
    if 'do not identify' in text:
        return 'No Disability'
    elif 'prefer not to specify' in text:
        return 'Prefer Not to Specify'
    else:
        return 'With Disability'

df['Disability_Category'] = df['Disability'].apply(categorize_disability)
filtered_df['Disability_Category'] = filtered_df['Disability'].apply(categorize_disability)

# ============= KPIs FIRST (smaller cards) =============
st.markdown("## 📌 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{len(filtered_df)}</div>
        <div class="metric-label">Total Responses (filtered)</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    avg_score_f = filtered_df['Recommendation_Score'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{avg_score_f:.1f if not np.isnan(avg_score_f) else 0:.1f}</div>
        <div class="metric-label">Avg Recommendation Score</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    low_scores_f = len(filtered_df[filtered_df['Recommendation_Score'] <= 4])
    high_scores_f = len(filtered_df[filtered_df['Recommendation_Score'] >= 8])
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{low_scores_f} / {high_scores_f}</div>
        <div class="metric-label">Low (≤4) / High (≥8) Scores</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    extremely_fulfilling_f = len(
        filtered_df[
            filtered_df['Work_Fulfillment'].str.contains('extremely', case=False, na=False)
        ]
    )
    pct_extremely_f = (extremely_fulfilling_f / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{pct_extremely_f:.1f}%</div>
        <div class="metric-label">"Extremely" Fulfilling (filtered)</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============= NOW KEY INSIGHTS BELOW KPIs =============
st.markdown("## 🔍 Key Insights & Patterns")

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

recognized = df[df['Recognition'].str.contains('Yes, I do feel recognized', case=False, na=False)]
avg_recognized = recognized['Recommendation_Score'].mean()
not_recognized = df[df['Recognition'].str.contains("don't feel recognized and would prefer", case=False, na=False)]
avg_not_recognized = not_recognized['Recommendation_Score'].mean() if len(not_recognized) > 0 else 0

col_ins1, col_ins2 = st.columns(2)

with col_ins1:
    st.markdown("### 📊 Overall Patterns")

    diff_fulfillment = avg_score_extremely - avg_score_not_extremely
    if not np.isnan(diff_fulfillment) and diff_fulfillment > 2:
        st.markdown(f"""
        <div class="insight-card insight-positive">
            <strong>✅ Strong Positive Link:</strong> Employees who find work "extremely fulfilling"
            score <strong>{diff_fulfillment:.1f} points higher</strong>
            ({avg_score_extremely:.1f} vs {avg_score_not_extremely:.1f}) on recommendation.
        </div>
        """, unsafe_allow_html=True)

    if avg_not_recognized > 0:
        diff_recognition = avg_recognized - avg_not_recognized
        if abs(diff_recognition) > 1.5:
            insight_class = "insight-positive" if diff_recognition > 0 else "insight-negative"
            icon = "✅" if diff_recognition > 0 else "⚠️"
            direction = "higher" if diff_recognition > 0 else "lower"
            st.markdown(f"""
            <div class="insight-card {insight_class}">
                <strong>{icon} Recognition Impact:</strong>
                Employees who feel recognized score <strong>{abs(diff_recognition):.1f} points {direction}</strong>
                ({avg_recognized:.1f} vs {avg_not_recognized:.1f}).
            </div>
            """, unsafe_allow_html=True)

    if lowest_role is not None:
        st.markdown(f"""
        <div class="insight-card insight-negative">
            <strong>⚠️ Lowest Scoring Role:</strong> {lowest_role}
            (avg: {role_scores.loc[lowest_role, 'mean']:.1f}, n={int(role_scores.loc[lowest_role, 'count'])})
        </div>
        """, unsafe_allow_html=True)

    if highest_role is not None:
        st.markdown(f"""
        <div class="insight-card insight-positive">
            <strong>✅ Highest Scoring Role:</strong> {highest_role}
            (avg: {role_scores.loc[highest_role, 'mean']:.1f}, n={int(role_scores.loc[highest_role, 'count'])})
        </div>
        """, unsafe_allow_html=True)

with col_ins2:
    st.markdown("### 👥 Demographic Patterns")

    if {'With Disability', 'No Disability'} <= set(disability_scores.index):
        diff_disability = (
            disability_scores.loc['No Disability', 'mean']
            - disability_scores.loc['With Disability', 'mean']
        )
        if abs(diff_disability) > 1:
            insight_class = "insight-negative" if diff_disability > 0 else "insight-positive"
            icon = "⚠️" if diff_disability > 0 else "✅"
            st.markdown(f"""
            <div class="insight-card {insight_class}">
                <strong>{icon} Disability Status:</strong>
                Employees with disabilities score
                <strong>{abs(diff_disability):.1f} points lower</strong>
                ({disability_scores.loc['With Disability', 'mean']:.1f} vs
                {disability_scores.loc['No Disability', 'mean']:.1f}).
            </div>
            """, unsafe_allow_html=True)

    ethnicity_scores = df.groupby('Ethnicity')['Recommendation_Score'].agg(['mean', 'count']).round(2)
    ethnicity_scores = ethnicity_scores[ethnicity_scores['count'] >= 5]
    if len(ethnicity_scores) > 0:
        top_ethnicity = ethnicity_scores['mean'].idxmax()
        top_ethnicity_short = top_ethnicity.split('(')[0].strip() if '(' in top_ethnicity else top_ethnicity[:40]
        st.markdown(f"""
        <div class="insight-card insight-positive">
            <strong>✅ Highest Scoring Ethnicity:</strong> {top_ethnicity_short}
            (avg: {ethnicity_scores.loc[top_ethnicity, 'mean']:.1f}, n={int(ethnicity_scores.loc[top_ethnicity, 'count'])})
        </div>
        """, unsafe_allow_html=True)

    low_scores_all = df[df['Recommendation_Score'] <= 4]
    if len(low_scores_all) > 0:
        low_score_roles = low_scores_all['Role'].value_counts().head(1)
        st.markdown(f"""
        <div class="insight-card insight-neutral">
            <strong>📌 Low Score Concentration:</strong> {low_score_roles.index[0]} has
            {low_score_roles.values[0]} responses with scores ≤4.
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# From here you can keep the rest of your sections (question breakdown, tabs, etc.) unchanged.
