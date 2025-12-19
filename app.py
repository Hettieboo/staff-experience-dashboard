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
    st.markdown("*Shows the percentage of positive responses for each role across all survey questions*")
    
    # Get top roles
    top_roles = df['Role'].value_counts().head(10).index.tolist()
    df_cross = df[df['Role'].isin(top_roles)].copy()
    df_cross['Role_Short'] = df_cross['Role'].apply(shorten_role)
    
    # Calculate positive response percentages for each question
    def calc_positive_pct(group_df, column, positive_keywords):
        """Calculate percentage of positive responses"""
        total = len(group_df)
        if total == 0:
            return 0
        positive = sum(group_df[column].str.contains('|'.join(positive_keywords), case=False, na=False))
        return (positive / total) * 100
    
    # Define what counts as "positive" for each question
    fulfillment_positive = ['extremely fulfilling']
    recognition_positive = ['Yes, I do feel recognized']
    growth_positive = ['Yes, I do feel there is potential']
    
    # Build the heatmap data
    heatmap_data = []
    role_labels = []
    
    for role in sorted(df_cross['Role_Short'].unique()):
        role_data = df_cross[df_cross['Role_Short'] == role]
        
        row = [
            calc_positive_pct(role_data, 'Work_Fulfillment', fulfillment_positive),
            calc_positive_pct(role_data, 'Work_Fulfillment', ['fulfilling and rewarding in some parts']),
            calc_positive_pct(role_data, 'Work_Fulfillment', ['somewhat fulfilling']),
            calc_positive_pct(role_data, 'Recognition', recognition_positive),
            calc_positive_pct(role_data, 'Recognition', ['somewhat feel recognized']),
            calc_positive_pct(role_data, 'Growth_Potential', growth_positive),
            calc_positive_pct(role_data, 'Growth_Potential', ['some potential to grow']),
            role_data['Recommendation_Score'].mean()
        ]
        
        heatmap_data.append(row)
        role_labels.append(role)
    
    # Question labels - compact and wrapped
    question_labels = [
        'Extremely<br>Fulfilling<br>Work',
        'Mixed<br>Fulfillment<br>Work',
        'Somewhat<br>Fulfilling<br>Work',
        'Yes, Feel<br>Recognized',
        'Somewhat<br>Recognized',
        'Yes, Growth<br>Potential',
        'Some Growth<br>Potential',
        'Avg Score<br>(0-10)'
    ]
    
    # Create heatmap
    heatmap_array = np.array(heatmap_data)
    
    # Normalize the last column (Recommendation Score) to 0-100 scale for color consistency
    heatmap_display = heatmap_array.copy()
    heatmap_display[:, -1] = heatmap_display[:, -1] * 10  # Scale 0-10 to 0-100
    
    # Create text labels
    text_labels = []
    for i, row in enumerate(heatmap_array):
        text_row = []
        for j, val in enumerate(row):
            if j == len(row) - 1:  # Last column is score
                text_row.append(f'{val:.1f}')
            else:  # Others are percentages
                text_row.append(f'{val:.0f}%')
        text_labels.append(text_row)
    
    fig_cross = go.Figure(data=go.Heatmap(
        z=heatmap_display,
        x=question_labels,
        y=role_labels,
        colorscale='RdYlGn',
        text=text_labels,
        texttemplate='%{text}',
        textfont={"size": 11, "color": "white"},
        colorbar=dict(
            title="Response<br>Rate (%)", 
            len=0.7,
            tickvals=[0, 25, 50, 75, 100],
            ticktext=["0%", "25%", "50%", "75%", "100%"]
        ),
        hovertemplate='<b>%{y}</b><br>%{x}<br>Value: %{text}<extra></extra>'
    ))
    
    fig_cross.update_layout(
        title="Complete Cross-Analysis: How Each Role Responds to Each Question",
        xaxis_title='Survey Questions',
        yaxis_title='Role / Department',
        height=650,
        margin=dict(l=200, r=50, t=100, b=100),
        xaxis=dict(tickangle=0, tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=11))
    )
    
    st.plotly_chart(fig_cross, use_container_width=True)
    
    # 🔹 Insights
    st.markdown("### 📝 Key Insights from Cross-Analysis")
    
    # Find best and worst performing roles
    avg_scores = df_cross.groupby('Role_Short')['Recommendation_Score'].mean().sort_values(ascending=False)
    
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
    st.markdown("**How to Read This Chart:**")
    st.markdown("- 🟢 **Green (50%+)**: Most employees in this role gave positive responses")
    st.markdown("- 🟡 **Yellow (25-50%)**: Mixed responses from this role")
    st.markdown("- 🔴 **Red (0-25%)**: Few positive responses - needs immediate attention")
    st.markdown("")
    st.markdown("**Actionable Recommendations:**")
    st.markdown("- Focus interventions on roles showing red/yellow across multiple questions")
    st.markdown("- Roles with high fulfillment but low growth perception may need career development programs")
    st.markdown("- Roles with low recognition should be prioritized for acknowledgment initiatives")

# ------------------- VARIED CHART TYPES -------------------
st.markdown("## 🏗 Response Distribution by Role")

def create_stacked_bar(df, value_col, title, orientation='h'):
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
        if orientation == 'h':
            x_vals, y_vals = cross_tab[col], cross_tab.index
            textposition = 'inside'
        else:
            x_vals, y_vals = cross_tab.index, cross_tab[col]
            textposition = 'auto'
        text_values = [f'{v:.1f}%' if v>5 else '' for v in cross_tab[col]]
        fig.add_trace(go.Bar(
            x=x_vals if orientation=='h' else y_vals,
            y=y_vals if orientation=='h' else x_vals,
            name=shorten_text(str(col), 30),
            orientation=orientation,
            text=text_values,
            textposition=textposition,
            textfont=dict(color='white', size=11),
            marker_color=colors[idx % len(colors)]
        ))
    
    fig.update_layout(
        barmode='stack',
        title=dict(text=title, font=dict(size=16, color='#2c3e50')),
        xaxis=dict(
            title='Percentage of Responses' if orientation=='h' else 'Role',
            range=[0,100] if orientation=='h' else None,
            showline=True,
            linewidth=2,
            linecolor='#34495e',
            showgrid=True,
            gridcolor='#ecf0f1',
            zeroline=True
        ),
        yaxis=dict(
            title='Role' if orientation=='h' else 'Percentage of Responses',
            range=[0,100] if orientation=='v' else None,
            showline=True,
            linewidth=2,
            linecolor='#34495e',
            showgrid=True,
            gridcolor='#ecf0f1'
        ),
        height=max(500, 60*len(cross_tab)+150) if orientation=='h' else 600,
        margin=dict(l=200, r=50, t=100, b=150),
        legend=dict(
            title='Response',
            traceorder='normal',
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#34495e',
            borderwidth=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='#f8f9fa'
    )
    
    # Add frame around the plot
    fig.update_xaxes(mirror=True, ticks='outside', showline=True, linecolor='#34495e', linewidth=2)
    fig.update_yaxes(mirror=True, ticks='outside', showline=True, linecolor='#34495e', linewidth=2)
    
    return fig

def create_grouped_bar(df, value_col, title):
    """Create grouped bar chart for comparison"""
    role_counts = df['Role'].value_counts().head(6)
    top_roles = role_counts.index.tolist()
    df_filtered_local = df[df['Role'].isin(top_roles)]
    df_filtered_local['Role_Short'] = df_filtered_local['Role'].apply(shorten_role)
    cross_tab = pd.crosstab(df_filtered_local['Role_Short'], df_filtered_local[value_col], normalize='index')*100
    
    fig = go.Figure()
    colors = px.colors.qualitative.Pastel
    
    for idx, col in enumerate(cross_tab.columns):
        fig.add_trace(go.Bar(
            x=cross_tab.index,
            y=cross_tab[col],
            name=shorten_text(str(col), 25),
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
        margin=dict(l=100, r=50, t=100, b=150),
        legend=dict(
            title='Response',
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

# Chart 1: Horizontal Stacked Bar
st.plotly_chart(create_stacked_bar(df, 'Work_Fulfillment', '💼 Work Fulfillment Distribution by Role', orientation='h'), use_container_width=True)

# Chart 2: Vertical Stacked Bar (Different style)
st.plotly_chart(create_stacked_bar(df, 'Recognition', '🌟 Recognition Distribution by Role', orientation='v'), use_container_width=True)

# Chart 3: Grouped Bar Chart (Side-by-side comparison)
st.plotly_chart(create_grouped_bar(df, 'Growth_Potential', '📈 Growth Potential Distribution by Role (Grouped)'), use_container_width=True)

# 🔹 Stacked Bar Insights
role_scores = df_insights.groupby('Role')['Recommendation_Score'].mean().sort_values()
extreme_roles = df_insights[df_insights['Work_Fulfillment'].str.contains('extremely', case=False, na=False)]['Role_Short'].unique()
st.markdown("### 📝 Insights & Recommendations")
st.markdown("- Roles with highest percentages of 'Extremely' fulfilling responses: " + ", ".join(extreme_roles))
st.markdown("- Roles with lowest recommendation scores: " + ", ".join(role_scores.head(3).index))
st.markdown("- Consider targeted interventions for roles with consistently low scores in Work Fulfillment, Recognition, or Growth Potential.")
