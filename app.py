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

# ================= CROSS-ANALYSIS / ROLE COMPARISONS =================
st.markdown("## 📈 Cross-Analysis: Demographics vs. Employee Sentiment")
tab1, tab2, tab3 = st.tabs(["🎯 Score Comparisons", "🔥 Sentiment Heatmap", "🔗 Correlation Analysis"])

# =================== INSIGHTS HELPERS ===================
# Create a separate copy for insights to avoid NameError
df_insights = filtered_df.copy()
df_insights['Role_Short'] = df_insights['Role'].apply(shorten_role)

# ------------------- HEATMAP -------------------
with tab2:
    st.markdown("### Sentiment Heatmaps: Role × Survey Questions")
    
    def create_sentiment_heatmap(df, question_col, title):
        top_roles = df['Role'].value_counts().head(8).index.tolist()
        df_filtered_local = df[df['Role'].isin(top_roles)]
        df_filtered_local['Role_Short'] = df_filtered_local['Role'].apply(shorten_role)
        cross_tab = pd.crosstab(df_filtered_local['Role_Short'], df_filtered_local[question_col], normalize='index')*100
        positive_cols = [col for col in cross_tab.columns if 'extremely' in str(col).lower() or 'yes' in str(col).lower()]
        if positive_cols:
            cross_tab = cross_tab.sort_values(by=positive_cols[0], ascending=True)
        fig = go.Figure(data=go.Heatmap(
            z=cross_tab.values,
            x=[col[:50]+'...' if len(str(col))>50 else str(col) for col in cross_tab.columns],
            y=cross_tab.index,
            colorscale='RdYlGn',
            text=[[f'{val:.1f}%' for val in row] for row in cross_tab.values],
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

    # 🔹 Heatmap Insights
    top_roles_positive = df_insights[df_insights['Work_Fulfillment'].str.contains('extremely', case=False, na=False)]['Role_Short'].unique()
    st.markdown("### 📝 Insights & Recommendations")
    st.markdown("- Positive sentiment is highest among roles: " + ", ".join(top_roles_positive))
    st.markdown("- Roles showing lower recognition and growth potential should be prioritized for recognition programs or professional development.")

# ------------------- TAB 3: CORRELATION ANALYSIS (NEW VERSION) -------------------
with tab3:
    st.markdown("### Comprehensive Cross-Analysis: All Groups × All Questions")
    st.markdown("*Diverging bars show positive (right) vs negative (left) sentiment for each role*")
    
    # Get top roles
    top_roles = df['Role'].value_counts().head(8).index.tolist()
    df_cross = df[df['Role'].isin(top_roles)].copy()
    df_cross['Role_Short'] = df_cross['Role'].apply(shorten_role)
    
    # Function to create diverging bar for each question
    def create_diverging_bar(df, question_col, title, positive_keywords, neutral_keywords, negative_keywords):
        """Create diverging stacked bar chart"""
        role_data = []
        roles = sorted(df['Role_Short'].unique())
        
        for role in roles:
            role_subset = df[df['Role_Short'] == role]
            total = len(role_subset)
            
            if total == 0:
                continue
            
            # Calculate percentages
            positive = sum(role_subset[question_col].str.contains('|'.join(positive_keywords), case=False, na=False)) / total * 100
            neutral = sum(role_subset[question_col].str.contains('|'.join(neutral_keywords), case=False, na=False)) / total * 100
            negative = sum(role_subset[question_col].str.contains('|'.join(negative_keywords), case=False, na=False)) / total * 100
            
            role_data.append({
                'Role': role,
                'Positive': positive,
                'Neutral': neutral,
                'Negative': negative
            })
        
        df_chart = pd.DataFrame(role_data)
        
        fig = go.Figure()
        
        # Negative bars (left side)
        fig.add_trace(go.Bar(
            y=df_chart['Role'],
            x=-df_chart['Negative'],
            name='Negative',
            orientation='h',
            marker=dict(color='#e74c3c'),
            text=[f'{val:.0f}%' if val > 5 else '' for val in df_chart['Negative']],
            textposition='inside',
            textfont=dict(color='white', size=11),
            hovertemplate='<b>%{y}</b><br>Negative: %{x:.1f}%<extra></extra>'
        ))
        
        # Neutral bars (center)
        fig.add_trace(go.Bar(
            y=df_chart['Role'],
            x=df_chart['Neutral'],
            name='Neutral',
            orientation='h',
            marker=dict(color='#f39c12'),
            text=[f'{val:.0f}%' if val > 5 else '' for val in df_chart['Neutral']],
            textposition='inside',
            textfont=dict(color='white', size=11),
            hovertemplate='<b>%{y}</b><br>Neutral: %{x:.1f}%<extra></extra>'
        ))
        
        # Positive bars (right side)
        fig.add_trace(go.Bar(
            y=df_chart['Role'],
            x=df_chart['Positive'],
            name='Positive',
            orientation='h',
            marker=dict(color='#27ae60'),
            text=[f'{val:.0f}%' if val > 5 else '' for val in df_chart['Positive']],
            textposition='inside',
            textfont=dict(color='white', size=11),
            hovertemplate='<b>%{y}</b><br>Positive: %{x:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            barmode='relative',
            title=dict(text=title, font=dict(size=16, color='#2c3e50')),
            xaxis=dict(
                title='← Negative    |    Positive →',
                range=[-100, 100],
                tickvals=[-100, -75, -50, -25, 0, 25, 50, 75, 100],
                ticktext=['100%', '75%', '50%', '25%', '0', '25%', '50%', '75%', '100%'],
                showline=True,
                linewidth=2,
                linecolor='#34495e',
                showgrid=True,
                gridcolor='#ecf0f1',
                zeroline=True,
                zerolinewidth=3,
                zerolinecolor='#34495e'
            ),
            yaxis=dict(
                title='Role / Department',
                showline=True,
                linewidth=2,
                linecolor='#34495e',
                showgrid=False
            ),
            height=500,
            margin=dict(l=200, r=50, t=80, b=80),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5,
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor='#34495e',
                borderwidth=1
            ),
            plot_bgcolor='white',
            paper_bgcolor='#f8f9fa'
        )
        
        fig.update_xaxes(mirror=True, ticks='outside', showline=True, linecolor='#34495e', linewidth=2)
        fig.update_yaxes(mirror=True, ticks='outside', showline=True, linecolor='#34495e', linewidth=2)
        
        return fig
    
    # Work Fulfillment
    st.subheader("💼 Work Fulfillment by Role")
    fig_fulfill = create_diverging_bar(
        df_cross, 
        'Work_Fulfillment',
        'Work Fulfillment Sentiment Balance',
        positive_keywords=['extremely fulfilling'],
        neutral_keywords=['somewhat', 'in some parts'],
        negative_keywords=["don't find the work", "taking steps to change"]
    )
    st.plotly_chart(fig_fulfill, use_container_width=True)
    
    # Recognition
    st.subheader("🌟 Recognition by Role")
    fig_recog = create_diverging_bar(
        df_cross, 
        'Recognition',
        'Recognition Sentiment Balance',
        positive_keywords=['Yes, I do feel recognized'],
        neutral_keywords=['somewhat', 'rare', 'prefer it that way'],
        negative_keywords=["don't feel recognized and would prefer"]
    )
    st.plotly_chart(fig_recog, use_container_width=True)
    
    # Growth Potential
    st.subheader("📈 Growth Potential by Role")
    fig_growth = create_diverging_bar(
        df_cross, 
        'Growth_Potential',
        'Growth Potential Sentiment Balance',
        positive_keywords=['Yes, I do feel there is potential'],
        neutral_keywords=['some potential', 'not interested in career growth'],
        negative_keywords=['limited', 'very little']
    )
    st.plotly_chart(fig_growth, use_container_width=True)
    
    # 🔹 Insights
    st.markdown("### 📝 Key Insights from Cross-Analysis")
    
    # Find best and worst performing roles
    avg_scores = df_cross.groupby('Role_Short')['Recommendation_Score'].mean().sort_values(ascending=False)
    
    st.markdown("**How to Read These Charts:**")
    st.markdown("- 🟢 **Green (Right)**: Positive responses - employees satisfied")
    st.markdown("- 🟡 **Yellow (Center)**: Neutral/Mixed responses")
    st.markdown("- 🔴 **Red (Left)**: Negative responses - employees dissatisfied")
    st.markdown("- The longer the green bar, the more satisfied that role is")
    
    st.markdown("")
    st.markdown("**Highest Satisfaction Roles:**")
    for role in avg_scores.head(3).index:
        score = avg_scores[role]
        st.markdown(f"- **{role}**: {score:.1f}/10 average recommendation score")
    
    st.markdown("")
    st.markdown("**Areas Needing Attention:**")
    for role in avg_scores.tail(3).index:
        score = avg_scores[role]
        st.markdown(f"- **{role}**: {score:.1f}/10 average recommendation score")
    
    st.markdown("")
    st.markdown("**Actionable Recommendations:**")
    st.markdown("- Roles showing more RED than GREEN need immediate attention")
    st.markdown("- Focus on roles with consistent negative sentiment across multiple questions")
    st.markdown("- Use insights to tailor interventions: recognition programs, career development, work redesign")

# ------------------- VARIED CHART TYPES -------------------
st.markdown("## 🏗 Response Distribution by Role")

def create_stacked_bar(df, value_col, title, orientation='v'):
    role_counts = df['Role'].value_counts().head(8)
    top_roles = role_counts.index.tolist()
    df_filtered_local = df[df['Role'].isin(top_roles)]
    df_filtered_local['Role_Short'] = df_filtered_local['Role'].apply(shorten_role)
    cross_tab = pd.crosstab(df_filtered_local['Role_Short'], df_filtered_local[value_col], normalize='index')*100
    role_short_order = [shorten_role(r) for r in top_roles]
    cross_tab = cross_tab.reindex(role_short_order)
    
    fig = go.Figure()
    colors = px.colors.qualitative.Set3
    
    for idx, col in enumerate(cross_tab.columns):
        # Shorten legend labels for readability
        short_label = str(col)[:45] + '...' if len(str(col)) > 45 else str(col)
        
        if orientation == 'v':
            x_vals, y_vals = cross_tab.index, cross_tab[col]
            textposition = 'inside'
        else:
            x_vals, y_vals = cross_tab[col], cross_tab.index
            textposition = 'inside'
            
        text_values = [f'{v:.1f}%' if v>5 else '' for v in cross_tab[col]]
        fig.add_trace(go.Bar(
            x=x_vals,
            y=y_vals,
            name=short_label,
            orientation='v' if orientation=='v' else 'h',
            text=text_values,
            textposition=textposition,
            textfont=dict(color='white', size=11),
            marker_color=colors[idx % len(colors)],
            marker_line_color='#34495e',
            marker_line_width=1
        ))
    
    fig.update_layout(
        barmode='stack',
        title=dict(text=title, font=dict(size=16, color='#2c3e50')),
        xaxis=dict(
            title='Role' if orientation=='v' else 'Percentage of Responses',
            range=None if orientation=='v' else [0,100],
            showline=True,
            linewidth=2,
            linecolor='#34495e',
            showgrid=False if orientation=='v' else True,
            gridcolor='#ecf0f1',
            tickangle=-30 if orientation=='v' else 0
        ),
        yaxis=dict(
            title='Percentage of Responses' if orientation=='v' else 'Role',
            range=[0,105] if orientation=='v' else None,
            showline=True,
            linewidth=2,
            linecolor='#34495e',
            showgrid=True,
            gridcolor='#ecf0f1'
        ),
        height=600,
        margin=dict(l=100, r=250, t=100, b=150),
        legend=dict(
            title='Response Type',
            traceorder='normal',
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#34495e',
            borderwidth=1,
            x=1.02,
            y=1,
            xanchor='left',
            yanchor='top',
            font=dict(size=10)
        ),
        plot_bgcolor='white',
        paper_bgcolor='#f8f9fa'
    )
    
    # Add frame around the plot
    fig.update_xaxes(mirror=True, ticks='outside', showline=True, linecolor='#34495e', linewidth=2)
    fig.update_yaxes(mirror=True, ticks='outside', showline=True, linecolor='#34495e', linewidth=2)
    
    return fig

def create_grouped_bar(df, value_col, title, color_scheme='pastel'):
    """Create grouped bar chart for comparison"""
    role_counts = df['Role'].value_counts().head(6)
    top_roles = role_counts.index.tolist()
    df_filtered_local = df[df['Role'].isin(top_roles)]
    df_filtered_local['Role_Short'] = df_filtered_local['Role'].apply(shorten_role)
    cross_tab = pd.crosstab(df_filtered_local['Role_Short'], df_filtered_local[value_col], normalize='index')*100
    
    fig = go.Figure()
    
    # Different color schemes
    if color_scheme == 'pastel':
        colors = px.colors.qualitative.Pastel
    elif color_scheme == 'vivid':
        colors = ['#e74c3c', '#f39c12', '#3498db', '#9b59b6', '#1abc9c', '#e67e22']
    else:
        colors = px.colors.qualitative.Set2
    
    # Shorten legend labels
    for idx, col in enumerate(cross_tab.columns):
        short_label = str(col)[:40] + '...' if len(str(col)) > 40 else str(col)
        
        fig.add_trace(go.Bar(
            x=cross_tab.index,
            y=cross_tab[col],
            name=short_label,
            text=[f'{v:.1f}%' if v>3 else '' for v in cross_tab[col]],
            textposition='outside',
            marker_color=colors[idx % len(colors)],
            marker_line_color='#34495e',
            marker_line_width=1.5
        ))
    
    fig.update_layout(
        barmode='group',
        title=dict(text=title, font=dict(size=16, color='#2c3e50')),
        xaxis=dict(
            title='Role',
            showline=True,
            linewidth=2,
            linecolor='#34495e',
            showgrid=False,
            tickangle=-30
        ),
        yaxis=dict(
            title='Percentage of Responses',
            range=[0,110],
            showline=True,
            linewidth=2,
            linecolor='#34495e',
            showgrid=True,
            gridcolor='#ecf0f1'
        ),
        height=550,
        margin=dict(l=100, r=250, t=100, b=150),
        legend=dict(
            title='Response Type',
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#34495e',
            borderwidth=1,
            x=1.02,
            y=1,
            xanchor='left',
            yanchor='top',
            font=dict(size=10)
        ),
        plot_bgcolor='white',
        paper_bgcolor='#f8f9fa'
    )
    
    fig.update_xaxes(mirror=True, ticks='outside', showline=True, linecolor='#34495e', linewidth=2)
    fig.update_yaxes(mirror=True, ticks='outside', showline=True, linecolor='#34495e', linewidth=2)
    
    return fig

# Chart 1: Horizontal Stacked Bar
st.plotly_chart(create_stacked_bar(df, 'Work_Fulfillment', '💼 Work Fulfillment Distribution by Role', orientation='h'), use_container_width=True)

# Chart 2: Grouped Bar Chart with vivid colors (Recognition)
st.plotly_chart(create_grouped_bar(df, 'Recognition', '🌟 Recognition Distribution by Role (Grouped)', color_scheme='vivid'), use_container_width=True)

# Chart 3: Grouped Bar Chart with pastel colors (Growth)
st.plotly_chart(create_grouped_bar(df, 'Growth_Potential', '📈 Growth Potential Distribution by Role (Grouped)', color_scheme='pastel'), use_container_width=True)

# 🔹 Stacked Bar Insights
role_scores = df_insights.groupby('Role')['Recommendation_Score'].mean().sort_values()
extreme_roles = df_insights[df_insights['Work_Fulfillment'].str.contains('extremely', case=False, na=False)]['Role_Short'].unique()
st.markdown("### 📝 Insights & Recommendations")
st.markdown("- Roles with highest percentages of 'Extremely' fulfilling responses: " + ", ".join(extreme_roles))
st.markdown("- Roles with lowest recommendation scores: " + ", ".join(role_scores.head(3).index))
st.markdown("- Consider targeted interventions for roles with consistently low scores in Work Fulfillment, Recognition, or Growth Potential.")
