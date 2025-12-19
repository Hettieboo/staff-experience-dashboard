import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page config
st.set_page_config(page_title="Homes First Survey Dashboard", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
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
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .section-header {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    /* Remove extra padding */
    .block-container {
        padding-top: 2rem;
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
st.sidebar.header("🔍 Filters")
st.sidebar.markdown("---")

# Role filter
roles = ['All'] + sorted(df['Role'].unique().tolist())
role_filter = st.sidebar.selectbox("👥 Role", roles)

# Ethnicity filter
ethnicities = ['All'] + sorted(df['Ethnicity'].unique().tolist())
ethnicity_filter = st.sidebar.selectbox("🌍 Ethnicity", ethnicities)

# Disability filter
disabilities = ['All'] + sorted(df['Disability'].unique().tolist())
disability_filter = st.sidebar.selectbox("♿ Disability", disabilities)

# Add info about filters
if role_filter != 'All' or ethnicity_filter != 'All' or disability_filter != 'All':
    st.sidebar.markdown("---")
    st.sidebar.info("🔎 Filters are active. Click 'All' to reset.")

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

# Helper function to shorten role names
def shorten_role(role):
    """Shorten long role names for better display"""
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

# Helper function to shorten answer text
def shorten_text(text, max_length=50):
    """Shorten long text for legends"""
    if len(text) <= max_length:
        return text
    # Smart truncation - try to break at word boundary
    truncated = text[:max_length-3]
    last_space = truncated.rfind(' ')
    if last_space > max_length * 0.7:  # If we can find a space in the last 30%
        truncated = truncated[:last_space]
    return truncated + '...'

# Helper function for stacked bar charts
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
    
    # Define a better color palette
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#fee140', '#30cfd0']
    
    for idx, col in enumerate(cross_tab.columns):
        # Only show percentage if > 5% to avoid clutter
        text_values = []
        for v in cross_tab[col]:
            if v > 5:
                text_values.append(f'{v:.1f}%')
            else:
                text_values.append('')
        
        fig.add_trace(go.Bar(
            name=shorten_text(col, 45),
            y=cross_tab.index,
            x=cross_tab[col],
            orientation='h',
            text=text_values,
            textposition='inside',
            textfont=dict(size=10, color='white'),
            marker_color=colors[idx % len(colors)],
            hovertemplate='<b>%{y}</b><br>' +
                         shorten_text(col, 45) + ': %{x:.1f}%<br>' +
                         '<extra></extra>'
        ))
    
    # Calculate dynamic height
    n_roles = len(cross_tab)
    chart_height = max(500, 60 * n_roles + 200)
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='#333')),
        barmode='stack',
        xaxis_title='Percentage (%)',
        yaxis_title='',
        height=chart_height,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=10),
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#ddd',
            borderwidth=1
        ),
        margin=dict(l=200, r=280, t=80, b=80),
        yaxis=dict(
            tickfont=dict(size=12),
            automargin=True
        ),
        xaxis=dict(
            tickfont=dict(size=11),
            range=[0, 100]
        ),
        plot_bgcolor='rgba(240,242,246,0.5)',
        paper_bgcolor='white'
    )
    
    return fig

# SECTION A: RECOMMENDATION SCORE
st.markdown('<div class="section-header"><h2>📊 How likely are you to recommend Homes First as a good place to work?</h2></div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    # 1. Overall score distribution (0-10)
    score_dist = filtered_df['Recommendation_Score'].value_counts().sort_index().reset_index()
    score_dist.columns = ['Score', 'Count']
    
    # Ensure all scores 0-10 are present
    all_scores = pd.DataFrame({'Score': range(11)})
    score_dist = all_scores.merge(score_dist, on='Score', how='left').fillna(0)
    score_dist['Count'] = score_dist['Count'].astype(int)
    
    # Color scale based on score
    colors_scale = []
    for score in score_dist['Score']:
        if score <= 3:
            colors_scale.append('#ef5350')
        elif score <= 6:
            colors_scale.append('#ffa726')
        elif score <= 8:
            colors_scale.append('#66bb6a')
        else:
            colors_scale.append('#42a5f5')
    
    fig1 = go.Figure(go.Bar(
        x=score_dist['Count'],
        y=score_dist['Score'],
        orientation='h',
        marker_color=colors_scale,
        text=score_dist['Count'],
        textposition='outside',
        hovertemplate='<b>Score %{y}</b><br>Count: %{x}<extra></extra>'
    ))
    
    fig1.update_layout(
        title=dict(text='Recommendation Score Distribution (0-10)', font=dict(size=16)),
        height=500,
        yaxis=dict(dtick=1, tickfont=dict(size=12), title='Score'),
        xaxis=dict(tickfont=dict(size=11), title='Count of Responses'),
        plot_bgcolor='rgba(240,242,246,0.5)',
        paper_bgcolor='white'
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # 2. Donut chart - score bands
    band_counts = filtered_df['Score_Band'].value_counts()
    band_order = ['0-3', '4-6', '7-8', '9-10']
    band_counts = band_counts.reindex(band_order, fill_value=0)
    
    fig2 = go.Figure(data=[go.Pie(
        labels=['Detractors (0-3)', 'Passive (4-6)', 'Promoters (7-8)', 'Strong Promoters (9-10)'],
        values=band_counts.values,
        hole=0.5,
        textinfo='label+percent',
        textfont=dict(size=12),
        marker=dict(
            colors=['#ef5350', '#ffa726', '#66bb6a', '#42a5f5'],
            line=dict(color='white', width=2)
        ),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    # Add annotation in the center
    total = band_counts.sum()
    fig2.add_annotation(
        text=f'<b>{total}</b><br>Total<br>Responses',
        x=0.5, y=0.5,
        font=dict(size=16, color='#333'),
        showarrow=False
    )
    
    fig2.update_layout(
        title=dict(text='Recommendation Score Bands', font=dict(size=16)),
        height=500,
        showlegend=True,
        legend=dict(font=dict(size=11), orientation='v')
    )
    st.plotly_chart(fig2, use_container_width=True)

# 3. 100% stacked horizontal bar - score bands by Role
st.subheader("📈 Score Bands by Role (Top 8 Roles)")
fig3 = create_stacked_bar(filtered_df, 'Score_Band', 'Recommendation Score Distribution by Role')
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# SECTION B: WORK FULFILLMENT
st.markdown('<div class="section-header"><h2>💼 How fulfilling and rewarding do you find your work?</h2></div>', unsafe_allow_html=True)
fig4 = create_stacked_bar(filtered_df, 'Work_Fulfillment', 'Work Fulfillment Distribution by Role')
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# SECTION C: RECOGNITION
st.markdown('<div class="section-header"><h2>🏆 Do you feel you get acknowledged and recognized for your contribution at work?</h2></div>', unsafe_allow_html=True)
fig5 = create_stacked_bar(filtered_df, 'Recognition', 'Recognition Sentiment by Role')
st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# SECTION D: GROWTH POTENTIAL
st.markdown('<div class="section-header"><h2>📈 Do you feel there is potential for growth at Homes First?</h2></div>', unsafe_allow_html=True)
fig6 = create_stacked_bar(filtered_df, 'Growth_Potential', 'Growth Potential Perception by Role')
st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")

# SECTION E: CONTEXT CHARTS - IMPROVED SIDE BY SIDE
st.markdown('<div class="section-header"><h2>👥 Respondent Demographics</h2></div>', unsafe_allow_html=True)

# Create tabs for better organization
tab1, tab2 = st.tabs(["🌍 Ethnicity Breakdown", "♿ Disability Breakdown"])

with tab1:
    # Ethnicity counts
    ethnicity_counts = filtered_df['Ethnicity'].value_counts().sort_values(ascending=False).head(15)
    
    # Shorten ethnicity labels for display
    ethnicity_display = {}
    for e in ethnicity_counts.index:
        short = e
        if len(e) > 60:
            # Shorten by removing parenthetical details
            if '(' in e:
                short = e.split('(')[0].strip()
        ethnicity_display[e] = short
    
    ethnicity_labels = [ethnicity_display[e] for e in ethnicity_counts.index]
    
    fig7 = go.Figure(go.Bar(
        y=ethnicity_labels,
        x=ethnicity_counts.values,
        orientation='h',
        marker=dict(
            color=ethnicity_counts.values,
            colorscale='Viridis',
            showscale=False,
            line=dict(color='white', width=1)
        ),
        text=ethnicity_counts.values,
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
    ))
    
    fig7.update_layout(
        title=dict(text=f'Ethnicity Distribution (Top 15, Total: {len(filtered_df)} Responses)', font=dict(size=16)),
        xaxis_title='Number of Responses',
        yaxis_title='',
        height=max(500, 40 * len(ethnicity_counts) + 150),
        margin=dict(l=250, r=80, t=80, b=50),
        yaxis=dict(tickfont=dict(size=11)),
        xaxis=dict(tickfont=dict(size=11)),
        plot_bgcolor='rgba(240,242,246,0.5)',
        paper_bgcolor='white'
    )
    st.plotly_chart(fig7, use_container_width=True)
    
    # Add download option
    if st.button("📥 Download Full Ethnicity Data"):
        csv = filtered_df['Ethnicity'].value_counts().to_csv()
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="ethnicity_data.csv",
            mime="text/csv"
        )

with tab2:
    # Disability counts
    disability_counts = filtered_df['Disability'].value_counts().sort_values(ascending=False).head(15)
    
    # Shorten disability labels
    disability_display = {}
    for d in disability_counts.index:
        short = d
        if len(d) > 70:
            short = d[:67] + '...'
        disability_display[d] = short
    
    disability_labels = [disability_display[d] for d in disability_counts.index]
    
    fig8 = go.Figure(go.Bar(
        y=disability_labels,
        x=disability_counts.values,
        orientation='h',
        marker=dict(
            color=disability_counts.values,
            colorscale='Teal',
            showscale=False,
            line=dict(color='white', width=1)
        ),
        text=disability_counts.values,
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
    ))
    
    fig8.update_layout(
        title=dict(text=f'Disability Status Distribution (Top 15, Total: {len(filtered_df)} Responses)', font=dict(size=16)),
        xaxis_title='Number of Responses',
        yaxis_title='',
        height=max(500, 40 * len(disability_counts) + 150),
        margin=dict(l=300, r=80, t=80, b=50),
        yaxis=dict(tickfont=dict(size=11)),
        xaxis=dict(tickfont=dict(size=11)),
        plot_bgcolor='rgba(240,242,246,0.5)',
        paper_bgcolor='white'
    )
    st.plotly_chart(fig8, use_container_width=True)
    
    # Add download option
    if st.button("📥 Download Full Disability Data"):
        csv = filtered_df['Disability'].value_counts().to_csv()
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="disability_data.csv",
            mime="text/csv"
        )

# Add footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>📊 Dashboard created for Homes First Society • Data represents employee survey responses</p>
    <p style='font-size: 0.9rem;'>Use filters in the sidebar to drill down into specific demographics</p>
</div>
""", unsafe_allow_html=True)
