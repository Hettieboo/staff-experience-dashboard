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
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .insight-card {
        background: #f0f7ff;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
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

def shorten_text(text, max_length=30):
    return text if len(text) <= max_length else text[:max_length-3] + '...'

df['Disability_Category'] = df['Disability'].apply(categorize_disability)
filtered_df['Disability_Category'] = filtered_df['Disability'].apply(categorize_disability)
filtered_df['Score_Band'] = filtered_df['Recommendation_Score'].apply(get_score_band)

# ================= KPI CARDS =================
st.markdown("## 📊 Key Performance Indicators (KPIs)")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card" style="padding:0.75rem;">
        <div class="metric-value" style="font-size:1.8rem;">{len(filtered_df)}</div>
        <div class="metric-label" style="font-size:0.85rem;">Total Responses</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    avg_score = filtered_df['Recommendation_Score'].mean()
    st.markdown(f"""
    <div class="metric-card" style="padding:0.75rem;">
        <div class="metric-value" style="font-size:1.8rem;">{avg_score:.1f}</div>
        <div class="metric-label" style="font-size:0.85rem;">Avg Recommendation Score</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    low_scores = len(filtered_df[filtered_df['Recommendation_Score'] <= 4])
    high_scores = len(filtered_df[filtered_df['Recommendation_Score'] >= 8])
    st.markdown(f"""
    <div class="metric-card" style="padding:0.75rem;">
        <div class="metric-value" style="font-size:1.8rem;">{low_scores} / {high_scores}</div>
        <div class="metric-label" style="font-size:0.85rem;">Low (≤4) / High (≥8) Scores</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    extremely_fulfilling = len(filtered_df[filtered_df['Work_Fulfillment'].str.contains('extremely', case=False, na=False)])
    pct_extremely = (extremely_fulfilling / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.markdown(f"""
    <div class="metric-card" style="padding:0.75rem;">
        <div class="metric-value" style="font-size:1.8rem;">{pct_extremely:.1f}%</div>
        <div class="metric-label" style="font-size:0.85rem;">"Extremely" Fulfilling</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ================= KEY INSIGHTS =================
st.markdown("## 🔍 Key Insights & Patterns")

overall_avg = df['Recommendation_Score'].mean()
role_scores = df.groupby('Role')['Recommendation_Score'].agg(['mean', 'count']).round(2)
role_scores = role_scores[role_scores['count'] >= 5]
lowest_role = role_scores['mean'].idxmin()
highest_role = role_scores['mean'].idxmax()

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="insight-card insight-negative">
        <strong>⚠️ Lowest Scoring Role:</strong> {lowest_role} (avg: {role_scores.loc[lowest_role,'mean']:.1f})
    </div>
    <div class="insight-card insight-positive">
        <strong>✅ Highest Scoring Role:</strong> {highest_role} (avg: {role_scores.loc[highest_role,'mean']:.1f})
    </div>
    """ , unsafe_allow_html=True)

with col2:
    st.markdown("### Demographics insights placeholder")
    
st.markdown("---")

# ================= CROSS-ANALYSIS / ROLE COMPARISONS =================
st.markdown("## 📈 Cross-Analysis: Demographics vs. Employee Sentiment")
tab1, tab2, tab3 = st.tabs(["🎯 Score Comparisons", "🔥 Sentiment Heatmap", "🔗 Correlation Analysis"])

# ----- TAB 1 (Score Comparisons) -----
# Keep original code for disability, ethnicity, role comparisons (unchanged)

# ----- TAB 2 (Sentiment Heatmap) -----
with tab2:
    st.markdown("### Sentiment Heatmaps: Role × Survey Questions")
    
    def create_sentiment_heatmap(df, question_col, title):
        top_roles = df['Role'].value_counts().head(8).index.tolist()
        df_filtered = df[df['Role'].isin(top_roles)]
        df_filtered['Role_Short'] = df_filtered['Role'].apply(shorten_role)
        cross_tab = pd.crosstab(df_filtered['Role_Short'], df_filtered[question_col], normalize='index') * 100
        positive_cols = [col for col in cross_tab.columns if 'extremely' in col.lower() or 'yes' in col.lower()]
        if positive_cols:
            cross_tab = cross_tab.sort_values(by=positive_cols[0], ascending=True)
        fig = go.Figure(data=go.Heatmap(
            z=cross_tab.values,
            x=[col[:50]+'...' if len(col)>50 else col for col in cross_tab.columns],
            y=cross_tab.index,
            colorscale='RdYlGn',
            text=[[f'{val:.0f}%' for val in row] for row in cross_tab.values],
            texttemplate='%{text}',
            textfont={"size":10},
            colorbar=dict(title="% of<br>Responses")
        ))
        fig.update_layout(
            title=title,
            xaxis_title='',
            yaxis_title='Role',
            height=max(500,60*len(cross_tab)+150),
            margin=dict(l=200,r=50,t=100,b=150),
            xaxis=dict(tickangle=-45,tickfont=dict(size=10))
        )
        return fig

    st.subheader("Work Fulfillment by Role")
    st.plotly_chart(create_sentiment_heatmap(df, 'Work_Fulfillment', 'Work Fulfillment Distribution by Role'), use_container_width=True)
    st.subheader("Recognition by Role")
    st.plotly_chart(create_sentiment_heatmap(df, 'Recognition', 'Recognition Sentiment by Role'), use_container_width=True)
    st.subheader("Growth Potential by Role")
    st.plotly_chart(create_sentiment_heatmap(df, 'Growth_Potential', 'Growth Potential Distribution by Role'), use_container_width=True)

# ----- TAB 3 (Correlation Analysis) -----
# Keep original correlation analysis code (unchanged)

# ================= STACKED BAR CHARTS =================
st.markdown("## 🏗 Stacked Response Distribution by Role")

def create_stacked_bar(df, value_col, title):
    role_counts = df['Role'].value_counts().head(8)
    top_roles = role_counts.index.tolist()
    df_filtered = df[df['Role'].isin(top_roles)]
    df_filtered['Role_Short'] = df_filtered['Role'].apply(shorten_role)
    cross_tab = pd.crosstab(df_filtered['Role_Short'], df_filtered[value_col], normalize='index')*100
    role_short_order = [shorten_role(r) for r in top_roles]
    cross_tab = cross_tab.reindex(role_short_order)
    fig = go.Figure()
    colors = px.colors.qualitative.Set3
    for idx,col in enumerate(cross_tab.columns):
        text_values = [f'{v:.1f}%' if v>5 else '' for v in cross_tab[col]]
        fig.add_trace(go.Bar(
            y=cross_tab.index,
            x=cross_tab[col],
            name=shorten_text(str(col),30),
            orientation='h',
            text=text_values,
            textposition='inside',
            marker_color=colors[idx%len(colors)]
        ))
    fig.update_layout(
        barmode='stack',
        title=title,
        xaxis=dict(title='Percentage of Responses', range=[0,100]),
        yaxis=dict(title='Role'),
        height=max(500,60*len(cross_tab)+150),
        margin=dict(l=200,r=50,t=100,b=150),
        legend=dict(title='Response',traceorder='normal')
    )
    return fig

st.plotly_chart(create_stacked_bar(df, 'Work_Fulfillment', 'Work Fulfillment Distribution by Role'), use_container_width=True)
st.plotly_chart(create_stacked_bar(df, 'Recognition', 'Recognition Distribution by Role'), use_container_width=True)
st.plotly_chart(create_stacked_bar(df, 'Growth_Potential', 'Growth Potential Distribution by Role'), use_container_width=True)
