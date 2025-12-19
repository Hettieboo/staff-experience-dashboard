import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="Homes First Survey Dashboard", layout="wide")

# Custom CSS
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
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel('Combined- Cross Analysis.xlsx')
    
    # Rename columns for easier use
    df.columns = ['Role', 'Ethnicity', 'Disability', 'Work_Fulfillment', 
                  'Recommendation_Score', 'Recognition', 'Growth_Potential']
    
    return df

df = load_data()

# Title
st.markdown('<div class="main-title">Homes First Employee Survey Dashboard</div>', unsafe_allow_html=True)

# Sidebar filters
st.sidebar.header("Filters")

# Role filter
roles = ['All'] + sorted(df['Role'].unique().tolist())
role_filter = st.sidebar.selectbox("Role", roles)

# Ethnicity filter
ethnicities = ['All'] + sorted(df['Ethnicity'].unique().tolist())
ethnicity_filter = st.sidebar.selectbox("Ethnicity", ethnicities)

# Disability filter
disabilities = ['All'] + sorted(df['Disability'].unique().tolist())
disability_filter = st.sidebar.selectbox("Disability", disabilities)

# Apply filters
filtered_df = df.copy()
if role_filter != 'All':
    filtered_df = filtered_df[filtered_df['Role'] == role_filter]
if ethnicity_filter != 'All':
    filtered_df = filtered_df[filtered_df['Ethnicity'] == ethnicity_filter]
if disability_filter != 'All':
    filtered_df = filtered_df[filtered_df['Disability'] == disability_filter]

# Metric cards
col1, col2, col3, col4 = st.columns(4)

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
        <div class="metric-value">{avg_score:.1f}</div>
        <div class="metric-label">Avg Recommendation Score</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    low_scores = len(filtered_df[filtered_df['Recommendation_Score'] <= 4])
    high_scores = len(filtered_df[filtered_df['Recommendation_Score'] >= 8])
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{low_scores} / {high_scores}</div>
        <div class="metric-label">Low (≤4) / High (≥8) Scores</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    extremely_fulfilling = len(filtered_df[filtered_df['Work_Fulfillment'].str.contains('extremely', case=False, na=False)])
    pct_extremely = (extremely_fulfilling / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{pct_extremely:.1f}%</div>
        <div class="metric-label">"Extremely" Fulfilling</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Helper function for score bands
def get_score_band(score):
    if score <= 3:
        return '0-3'
    elif score <= 6:
        return '4-6'
    elif score <= 8:
        return '7-8'
    else:
        return '9-10'

# Add score band column
filtered_df['Score_Band'] = filtered_df['Recommendation_Score'].apply(get_score_band)

# Helper function for stacked bar charts
def create_stacked_bar(df, value_col, title, height=None):
    # Get top 10 roles by count
    role_counts = df['Role'].value_counts().head(10)
    top_roles = role_counts.index.tolist()
    df_filtered = df[df['Role'].isin(top_roles)]
    
    # Calculate percentages
    cross_tab = pd.crosstab(df_filtered['Role'], df_filtered[value_col], normalize='index') * 100
    
    # Sort by total count
    cross_tab = cross_tab.loc[top_roles]
    
    # Create figure
    fig = go.Figure()
    
    for col in cross_tab.columns:
        fig.add_trace(go.Bar(
            name=col,
            y=cross_tab.index,
            x=cross_tab[col],
            orientation='h',
            text=[f'{v:.1f}%' for v in cross_tab[col]],
            textposition='inside'
        ))
    
    # Calculate dynamic height
    n_roles = len(cross_tab)
    chart_height = max(400, 45 * n_roles + 120) if height is None else height
    
    fig.update_layout(
        title=title,
        barmode='stack',
        xaxis_title='Percentage (%)',
        yaxis_title='Role',
        height=chart_height,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10)
        )
    )
    
    return fig

# SECTION A: RECOMMENDATION SCORE
st.header("How likely are you to recommend Homes First as a good place to work?")

col1, col2 = st.columns([1, 1])

with col1:
    # 1. Overall score distribution (0-10)
    score_dist = filtered_df['Recommendation_Score'].value_counts().sort_index().reset_index()
    score_dist.columns = ['Score', 'Count']
    
    # Ensure all scores 0-10 are present
    all_scores = pd.DataFrame({'Score': range(11)})
    score_dist = all_scores.merge(score_dist, on='Score', how='left').fillna(0)
    
    fig1 = px.bar(score_dist, x='Count', y='Score', orientation='h',
                  title='Recommendation Score Distribution (0-10)',
                  labels={'Count': 'Count', 'Score': 'Score'})
    fig1.update_layout(height=500, yaxis=dict(dtick=1))
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # 2. Donut chart - score bands
    band_counts = filtered_df['Score_Band'].value_counts()
    band_order = ['0-3', '4-6', '7-8', '9-10']
    band_counts = band_counts.reindex(band_order, fill_value=0)
    
    fig2 = go.Figure(data=[go.Pie(
        labels=band_counts.index,
        values=band_counts.values,
        hole=0.4,
        textinfo='label+percent',
        marker=dict(colors=['#ef5350', '#ffa726', '#66bb6a', '#42a5f5'])
    )])
    fig2.update_layout(title='Recommendation Score Bands', height=500)
    st.plotly_chart(fig2, use_container_width=True)

# 3. 100% stacked horizontal bar - score bands by Role
st.subheader("Recommendation Score Bands by Role (Top 10 Roles)")
fig3 = create_stacked_bar(filtered_df, 'Score_Band', 'Score Bands by Role')
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# SECTION B: WORK FULFILLMENT
st.header("How fulfilling and rewarding do you find your work?")
fig4 = create_stacked_bar(filtered_df, 'Work_Fulfillment', 'Work Fulfillment by Role (Top 10 Roles)')
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# SECTION C: RECOGNITION
st.header("Do you feel you get acknowledged and recognized for your contribution at work?")
fig5 = create_stacked_bar(filtered_df, 'Recognition', 'Recognition by Role (Top 10 Roles)')
st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# SECTION D: GROWTH POTENTIAL
st.header("Do you feel there is potential for growth at Homes First?")
fig6 = create_stacked_bar(filtered_df, 'Growth_Potential', 'Growth Potential by Role (Top 10 Roles)')
st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")

# SECTION E: CONTEXT CHARTS
st.header("Context: Ethnicity and Disability")

col1, col2 = st.columns([1, 1])

with col1:
    # Ethnicity counts
    ethnicity_counts = filtered_df['Ethnicity'].value_counts().sort_values(ascending=True)
    n_ethnicities = len(ethnicity_counts)
    eth_height = max(400, 45 * n_ethnicities + 120)
    
    fig7 = px.bar(ethnicity_counts, x=ethnicity_counts.values, y=ethnicity_counts.index,
                  orientation='h', title='Ethnicity Distribution',
                  labels={'x': 'Count', 'y': 'Ethnicity'})
    fig7.update_layout(height=eth_height)
    st.plotly_chart(fig7, use_container_width=True)

with col2:
    # Disability counts
    disability_counts = filtered_df['Disability'].value_counts().sort_values(ascending=True)
    n_disabilities = len(disability_counts)
    dis_height = max(400, 45 * n_disabilities + 120)
    
    fig8 = px.bar(disability_counts, x=disability_counts.values, y=disability_counts.index,
                  orientation='h', title='Disability Distribution',
                  labels={'x': 'Count', 'y': 'Disability'})
    fig8.update_layout(height=dis_height)
    st.plotly_chart(fig8, use_container_width=True)
