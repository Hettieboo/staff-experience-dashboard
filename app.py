import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

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

# Helper function to create disability categories
def categorize_disability(disability_text):
    if 'do not identify' in disability_text.lower():
        return 'No Disability'
    elif 'prefer not to specify' in disability_text.lower():
        return 'Prefer Not to Specify'
    else:
        return 'With Disability'

df['Disability_Category'] = df['Disability'].apply(categorize_disability)
filtered_df['Disability_Category'] = filtered_df['Disability'].apply(categorize_disability)

# ============= KEY INSIGHTS SECTION =============
st.markdown("## 🔍 Key Insights & Patterns")

# Calculate insights
overall_avg = df['Recommendation_Score'].mean()

# Insight 1: Disability impact
disability_scores = df.groupby('Disability_Category')['Recommendation_Score'].agg(['mean', 'count']).round(2)
disability_scores = disability_scores[disability_scores['count'] >= 5]  # Only groups with 5+ responses

# Insight 2: Role with lowest scores
role_scores = df.groupby('Role')['Recommendation_Score'].agg(['mean', 'count']).round(2)
role_scores = role_scores[role_scores['count'] >= 5]
lowest_role = role_scores['mean'].idxmin()
highest_role = role_scores['mean'].idxmax()

# Insight 3: Extremely fulfilling correlation
extremely_fulfilling = df[df['Work_Fulfillment'].str.contains('extremely', case=False, na=False)]
avg_score_extremely = extremely_fulfilling['Recommendation_Score'].mean()
not_extremely = df[~df['Work_Fulfillment'].str.contains('extremely', case=False, na=False)]
avg_score_not_extremely = not_extremely['Recommendation_Score'].mean()

# Insight 4: Recognition impact
recognized = df[df['Recognition'].str.contains('Yes, I do feel recognized', case=False, na=False)]
avg_recognized = recognized['Recommendation_Score'].mean()
not_recognized = df[df['Recognition'].str.contains("don't feel recognized and would prefer", case=False, na=False)]
avg_not_recognized = not_recognized['Recommendation_Score'].mean() if len(not_recognized) > 0 else 0

# Display insights
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Overall Patterns")
    
    # Work fulfillment correlation
    diff_fulfillment = avg_score_extremely - avg_score_not_extremely
    if diff_fulfillment > 2:
        st.markdown(f"""
        <div class="insight-card insight-positive">
            <strong>✅ Strong Positive Link:</strong> Employees who find work "extremely fulfilling" 
            score <strong>{diff_fulfillment:.1f} points higher</strong> ({avg_score_extremely:.1f} vs {avg_score_not_extremely:.1f}) 
            on recommendation likelihood.
        </div>
        """, unsafe_allow_html=True)
    
    # Recognition correlation
    if avg_not_recognized > 0:
        diff_recognition = avg_recognized - avg_not_recognized
        if abs(diff_recognition) > 1.5:
            insight_class = "insight-positive" if diff_recognition > 0 else "insight-negative"
            st.markdown(f"""
            <div class="insight-card {insight_class}">
                <strong>{'✅' if diff_recognition > 0 else '⚠️'} Recognition Impact:</strong> 
                Employees who feel recognized score <strong>{abs(diff_recognition):.1f} points 
                {'higher' if diff_recognition > 0 else 'lower'}</strong> 
                ({avg_recognized:.1f} vs {avg_not_recognized:.1f}).
            </div>
            """, unsafe_allow_html=True)
    
    # Role insights
    st.markdown(f"""
    <div class="insight-card insight-negative">
        <strong>⚠️ Lowest Scoring Role:</strong> {lowest_role} 
        (avg: {role_scores.loc[lowest_role, 'mean']:.1f})
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="insight-card insight-positive">
        <strong>✅ Highest Scoring Role:</strong> {highest_role} 
        (avg: {role_scores.loc[highest_role, 'mean']:.1f})
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("### 👥 Demographic Patterns")
    
    # Disability insights
    if 'With Disability' in disability_scores.index and 'No Disability' in disability_scores.index:
        diff_disability = disability_scores.loc['No Disability', 'mean'] - disability_scores.loc['With Disability', 'mean']
        if abs(diff_disability) > 1:
            insight_class = "insight-negative" if diff_disability > 0 else "insight-positive"
            st.markdown(f"""
            <div class="insight-card {insight_class}">
                <strong>{'⚠️' if diff_disability > 0 else '✅'} Disability Status:</strong> 
                Employees {'with' if diff_disability > 0 else 'without'} disabilities score 
                <strong>{abs(diff_disability):.1f} points lower</strong> 
                ({disability_scores.loc['With Disability', 'mean']:.1f} vs 
                {disability_scores.loc['No Disability', 'mean']:.1f}).
            </div>
            """, unsafe_allow_html=True)
    
    # Top ethnicity by score
    ethnicity_scores = df.groupby('Ethnicity')['Recommendation_Score'].agg(['mean', 'count']).round(2)
    ethnicity_scores = ethnicity_scores[ethnicity_scores['count'] >= 5]
    if len(ethnicity_scores) > 0:
        top_ethnicity = ethnicity_scores['mean'].idxmax()
        top_ethnicity_short = top_ethnicity.split('(')[0].strip() if '(' in top_ethnicity else top_ethnicity[:40]
        st.markdown(f"""
        <div class="insight-card insight-positive">
            <strong>✅ Highest Scoring Ethnicity:</strong> {top_ethnicity_short} 
            (avg: {ethnicity_scores.loc[top_ethnicity, 'mean']:.1f})
        </div>
        """, unsafe_allow_html=True)
    
    # Low score concentration
    low_scores = df[df['Recommendation_Score'] <= 4]
    if len(low_scores) > 0:
        low_score_roles = low_scores['Role'].value_counts().head(1)
        st.markdown(f"""
        <div class="insight-card insight-neutral">
            <strong>📌 Low Score Concentration:</strong> {low_score_roles.index[0]} has 
            {low_score_roles.values[0]} responses with scores ≤4.
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

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

# ============= CROSS-ANALYSIS SECTION =============
st.markdown("## 📈 Cross-Analysis: Demographics vs. Employee Sentiment")

tab1, tab2, tab3 = st.tabs(["🎯 Score Comparisons", "🔥 Sentiment Heatmap", "🔗 Correlation Analysis"])

with tab1:
    st.markdown("### Average Recommendation Score by Demographics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Disability comparison
        disability_comparison = df.groupby('Disability_Category')['Recommendation_Score'].agg(['mean', 'count']).reset_index()
        disability_comparison = disability_comparison[disability_comparison['count'] >= 3]
        disability_comparison = disability_comparison.sort_values('mean', ascending=True)
        
        fig_disability = go.Figure()
        fig_disability.add_hline(y=overall_avg, line_dash="dash", line_color="red", 
                                annotation_text=f"Overall Avg: {overall_avg:.1f}",
                                annotation_position="right")
        
        colors_disability = ['#ef5350' if x < overall_avg - 0.5 else '#66bb6a' if x > overall_avg + 0.5 else '#ffa726' 
                            for x in disability_comparison['mean']]
        
        fig_disability.add_trace(go.Bar(
            y=disability_comparison['Disability_Category'],
            x=disability_comparison['mean'],
            orientation='h',
            text=[f"{m:.1f} (n={int(c)})" for m, c in zip(disability_comparison['mean'], disability_comparison['count'])],
            textposition='outside',
            marker_color=colors_disability,
            hovertemplate='<b>%{y}</b><br>Avg Score: %{x:.1f}<extra></extra>'
        ))
        
        fig_disability.update_layout(
            title='Average Score by Disability Status',
            xaxis_title='Average Recommendation Score',
            yaxis_title='',
            height=300,
            showlegend=False,
            xaxis=dict(range=[0, 10])
        )
        
        st.plotly_chart(fig_disability, use_container_width=True)
    
    with col2:
        # Top 8 ethnicities by count
        ethnicity_comparison = df.groupby('Ethnicity')['Recommendation_Score'].agg(['mean', 'count']).reset_index()
        ethnicity_comparison = ethnicity_comparison[ethnicity_comparison['count'] >= 5]
        ethnicity_comparison = ethnicity_comparison.sort_values('count', ascending=False).head(8)
        ethnicity_comparison = ethnicity_comparison.sort_values('mean', ascending=True)
        
        # Shorten labels
        ethnicity_comparison['Ethnicity_Short'] = ethnicity_comparison['Ethnicity'].apply(
            lambda x: x.split('(')[0].strip()[:40] if '(' in x else x[:40]
        )
        
        colors_ethnicity = ['#ef5350' if x < overall_avg - 0.5 else '#66bb6a' if x > overall_avg + 0.5 else '#ffa726' 
                           for x in ethnicity_comparison['mean']]
        
        fig_ethnicity = go.Figure()
        
        fig_ethnicity.add_hline(y=overall_avg, line_dash="dash", line_color="red",
                               annotation_text=f"Overall Avg: {overall_avg:.1f}",
                               annotation_position="right")
        
        fig_ethnicity.add_trace(go.Bar(
            y=ethnicity_comparison['Ethnicity_Short'],
            x=ethnicity_comparison['mean'],
            orientation='h',
            text=[f"{m:.1f} (n={int(c)})" for m, c in zip(ethnicity_comparison['mean'], ethnicity_comparison['count'])],
            textposition='outside',
            marker_color=colors_ethnicity,
            hovertemplate='<b>%{y}</b><br>Avg Score: %{x:.1f}<extra></extra>'
        ))
        
        fig_ethnicity.update_layout(
            title='Average Score by Ethnicity (Top 8 by Count)',
            xaxis_title='Average Recommendation Score',
            yaxis_title='',
            height=300,
            showlegend=False,
            xaxis=dict(range=[0, 10]),
            margin=dict(l=180)
        )
        
        st.plotly_chart(fig_ethnicity, use_container_width=True)
    
    # Role comparison - full width
    st.markdown("### Average Score by Role")
    
    role_comparison = df.groupby('Role')['Recommendation_Score'].agg(['mean', 'count']).reset_index()
    role_comparison = role_comparison[role_comparison['count'] >= 5]
    role_comparison = role_comparison.sort_values('mean', ascending=True)
    
    # Shorten role names
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
    
    role_comparison['Role_Short'] = role_comparison['Role'].apply(shorten_role)
    
    colors_role = ['#ef5350' if x < overall_avg - 0.5 else '#66bb6a' if x > overall_avg + 0.5 else '#ffa726' 
                   for x in role_comparison['mean']]
    
    fig_role = go.Figure()
    
    fig_role.add_hline(y=overall_avg, line_dash="dash", line_color="red",
                      annotation_text=f"Overall Avg: {overall_avg:.1f}",
                      annotation_position="right")
    
    fig_role.add_trace(go.Bar(
        y=role_comparison['Role_Short'],
        x=role_comparison['mean'],
        orientation='h',
        text=[f"{m:.1f} (n={int(c)})" for m, c in zip(role_comparison['mean'], role_comparison['count'])],
        textposition='outside',
        marker_color=colors_role,
        hovertemplate='<b>%{y}</b><br>Avg Score: %{x:.1f}<extra></extra>'
    ))
    
    fig_role.update_layout(
        title='Average Score by Role (5+ Responses)',
        xaxis_title='Average Recommendation Score',
        yaxis_title='Role',
        height=max(500, 50*len(role_comparison)),
        showlegend=False,
        xaxis=dict(range=[0, 10]),
        margin=dict(l=200)
    )
    
    st.plotly_chart(fig_role, use_container_width=True)

# ================= STACKED BAR CHART HELPER =================
def shorten_text(text, max_length=30):
    return text if len(text) <= max_length else text[:max_length-3] + '...'

def create_stacked_bar(df, value_col, title):
    # Get top 8 roles by count
    role_counts = df['Role'].value_counts().head(8)
    top_roles = role_counts.index.tolist()
    df_filtered = df[df['Role'].isin(top_roles)]
    
    # Shorten role names
    df_filtered['Role_Short'] = df_filtered['Role'].apply(shorten_role)
    
    # Calculate percentages
    cross_tab = pd.crosstab(df_filtered['Role_Short'], df_filtered[value_col], normalize='index') * 100
    
    # Sort by original role order
    role_short_order = [shorten_role(r) for r in top_roles]
    cross_tab = cross_tab.reindex(role_short_order)
    
    # Create figure
    fig = go.Figure()
    
    # Define a color palette
    colors = px.colors.qualitative.Set3
    
    for idx, col in enumerate(cross_tab.columns):
        # Only show percentage if >5% to avoid clutter
        text_values = [f'{v:.1f}%' if v > 5 else '' for v in cross_tab[col]]
        fig.add_trace(go.Bar(
            y=cross_tab.index,
            x=cross_tab[col],
            name=shorten_text(str(col), max_length=30),
            orientation='h',
            text=text_values,
            textposition='inside',
            marker_color=colors[idx % len(colors)]
        ))
    
    fig.update_layout(
        barmode='stack',
        title=title,
        xaxis=dict(title='Percentage of Responses', range=[0, 100]),
        yaxis=dict(title='Role'),
        height=max(400, 50 * len(cross_tab) + 100),
        margin=dict(l=200, r=50, t=100, b=150),
        legend=dict(title='Response', traceorder='normal')
    )
    
    return fig

# Example: Stacked bars for Work Fulfillment, Recognition, Growth Potential
st.markdown("## 🏗 Stacked Response Distribution by Role")
fig_work = create_stacked_bar(df, 'Work_Fulfillment', 'Work Fulfillment Distribution by Role')
st.plotly_chart(fig_work, use_container_width=True)

fig_recognition = create_stacked_bar(df, 'Recognition', 'Recognition Distribution by Role')
st.plotly_chart(fig_recognition, use_container_width=True)

fig_growth = create_stacked_bar(df, 'Growth_Potential', 'Growth Potential Distribution by Role')
st.plotly_chart(fig_growth, use_container_width=True)
