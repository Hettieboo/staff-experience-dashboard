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

# Convert text responses to numeric scores
def convert_to_numeric(df):
    """Convert text survey responses to numeric values for correlation analysis"""
    df_numeric = df.copy()
    
    # Work Fulfillment scoring
    fulfillment_map = {
        'I find the work I do extremely fulfilling and rewarding': 5,
        'I find the work I do fulfilling and rewarding in some parts and not so much in others': 3,
        'I find the work I do somewhat fulfilling and rewarding': 3,
        "I don't find the work I do to be fulfilling or rewarding but I like other aspects of the job (such as the hours, the location, the pay/benefits, etc.)": 2,
        "I don't find the work I do to be fulfilling and rewarding so I am taking steps to change jobs/career path/industry": 1
    }
    df_numeric['Work_Fulfillment_Score'] = df_numeric['Work_Fulfillment'].map(fulfillment_map)
    
    # Recognition scoring
    recognition_map = {
        'Yes, I do feel recognized and acknowledged': 5,
        'I somewhat feel recognized and acknowledged': 3,
        'I do find myself being recognized and acknowledged, but it\'s rare given the contributions I make': 2,
        'I don\'t feel recognized and acknowledged and would prefer staff successes to be highlighted more frequently': 1,
        'I don\'t feel recognized and acknowledged but I prefer it that way': 2
    }
    df_numeric['Recognition_Score'] = df_numeric['Recognition'].map(recognition_map)
    
    # Growth Potential scoring
    growth_map = {
        'Yes, I do feel there is potential to grow and I hope to advance my career with Homes First': 5,
        'There is some potential to grow and I hope to advance my career with Homes First': 4,
        'I am not interested in career growth and prefer to remain in my current role': 3,
        'There is very little potential to grow although I would like to advance my career with Homes First': 2,
        'Potential to grow seems limited at Homes First and I will likely need to advance my career with another organization': 1
    }
    df_numeric['Growth_Potential_Score'] = df_numeric['Growth_Potential'].map(growth_map)
    
    return df_numeric

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
df_insights = filtered_df.copy()
df_insights['Role_Short'] = df_insights['Role'].apply(shorten_role)

# ------------------- TAB 1: SCORE COMPARISONS -------------------
with tab1:
    st.markdown("### Average Recommendation Scores Across Groups")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # By Role
        role_avg = df.groupby('Role')['Recommendation_Score'].agg(['mean', 'count']).reset_index()
        role_avg = role_avg[role_avg['count'] >= 3].sort_values('mean', ascending=True).tail(10)
        role_avg['Role_Short'] = role_avg['Role'].apply(shorten_role)
        
        fig1 = px.bar(role_avg, y='Role_Short', x='mean', orientation='h',
                     color='mean', color_continuous_scale='RdYlGn',
                     range_color=[0, 10], text='mean',
                     title="Average Score by Role (Top 10)")
        fig1.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig1.update_layout(xaxis_range=[0, 11], xaxis_title="Avg Score", yaxis_title="", height=400, showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # By Disability
        dis_avg = df.groupby('Disability_Category')['Recommendation_Score'].agg(['mean', 'count']).reset_index()
        dis_avg = dis_avg[dis_avg['count'] >= 5].sort_values('mean', ascending=True)
        
        fig2 = px.bar(dis_avg, y='Disability_Category', x='mean', orientation='h',
                     color='mean', color_continuous_scale='RdYlGn',
                     range_color=[0, 10], text='mean',
                     title="Average Score by Disability Status")
        fig2.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig2.update_layout(xaxis_range=[0, 11], xaxis_title="Avg Score", yaxis_title="", height=300, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

# ------------------- TAB 2: HEATMAP -------------------
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
    if len(top_roles_positive) > 0:
        st.markdown("- Positive sentiment is highest among roles: " + ", ".join(top_roles_positive[:5]))
    st.markdown("- Roles showing lower recognition and growth potential should be prioritized for recognition programs or professional development.")

# ------------------- TAB 3: CORRELATION ANALYSIS -------------------
with tab3:
    st.markdown("### Correlation Analysis: Survey Metrics")
    
    # Convert to numeric
    df_numeric = convert_to_numeric(df)
    
    # Select only the numeric score columns
    numeric_cols = ['Work_Fulfillment_Score', 'Recognition_Score', 'Growth_Potential_Score', 'Recommendation_Score']
    
    # Drop rows with NaN values in these columns
    df_corr = df_numeric[numeric_cols].dropna()
    
    # Calculate correlation
    corr_matrix = df_corr.corr()
    
    # Create correlation heatmap with FULL question text
    question_labels = [
        'How fulfilling and<br>rewarding do you find<br>your work?',
        'Do you feel you get<br>acknowledged and recognized<br>for your contribution at work?',
        'Do you feel there is<br>potential for growth<br>at Homes First?',
        'How likely are you to<br>recommend Homes First<br>as a good place to work?'
    ]
    
    # Convert correlation values to relationship strength labels
    def get_relationship_strength(val):
        if val == 1.0:
            return "Same Question"
        elif val >= 0.7:
            return f"Very Strong<br>({val:.2f})"
        elif val >= 0.5:
            return f"Strong<br>({val:.2f})"
        elif val >= 0.3:
            return f"Moderate<br>({val:.2f})"
        elif val >= 0.1:
            return f"Weak<br>({val:.2f})"
        else:
            return f"Very Weak<br>({val:.2f})"
    
    text_labels = [[get_relationship_strength(val) for val in row] for row in corr_matrix.values]
    
    fig_corr = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=question_labels,
        y=question_labels,
        colorscale='RdYlGn',
        zmid=0,
        zmin=-1,
        zmax=1,
        text=text_labels,
        texttemplate='%{text}',
        textfont={"size": 11, "color": "white"},
        colorbar=dict(
            title="Relationship<br>Strength", 
            len=0.7,
            tickvals=[0, 0.3, 0.5, 0.7, 1.0],
            ticktext=["Weak", "Moderate", "Strong", "Very Strong", "Perfect"]
        )
    ))
    
    fig_corr.update_layout(
        title="Question Relationship Analysis: Which Answers Tend to Go Together?",
        xaxis_title='',
        yaxis_title='',
        height=600,
        margin=dict(l=250, r=50, t=100, b=200),
        xaxis=dict(tickangle=-30, tickfont=dict(size=11)),
        yaxis=dict(tickfont=dict(size=11))
    )
    
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # 🔹 Correlation Insights
    st.markdown("### 📝 Key Insights")
    
    # Find strongest correlations (excluding diagonal)
    corr_pairs = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr_pairs.append({
                'Question 1': question_labels[i].replace('<br>', ' '),
                'Question 2': question_labels[j].replace('<br>', ' '),
                'Strength': corr_matrix.iloc[i, j]
            })
    
    corr_df = pd.DataFrame(corr_pairs).sort_values('Strength', ascending=False)
    
    def strength_label(val):
        if val >= 0.7:
            return "Very Strong"
        elif val >= 0.5:
            return "Strong"
        elif val >= 0.3:
            return "Moderate"
        else:
            return "Weak"
    
    st.markdown("**Strongest Relationships Between Questions:**")
    for idx, row in corr_df.head(3).iterrows():
        st.markdown(f"- **{strength_label(row['Strength'])}** relationship ({row['Strength']:.2f})")
        st.markdown(f"  - When employees answer positively to *'{row['Question 1']}'*")
        st.markdown(f"  - They also tend to answer positively to *'{row['Question 2']}'*")
        st.markdown("")
    
    st.markdown("**What This Means:**")
    st.markdown("- **Very Strong/Strong** (0.7-1.0): These questions are closely linked - improving one likely improves the other")
    st.markdown("- **Moderate** (0.3-0.7): Some connection exists between these areas")
    st.markdown("- **Weak** (0-0.3): These questions measure different aspects of employee experience")
    st.markdown("")
    st.markdown("**Actionable Recommendations:**")
    st.markdown("- Focus on the questions most strongly related to 'Recommend Homes First' - these have the biggest impact")
    st.markdown("- If two questions are strongly linked, solving one issue may help solve both")

# ------------------- STACKED BARS -------------------
st.markdown("---")
st.markdown("## 🏗 Response Distribution by Role")

def create_stacked_bar(df, value_col, title):
    role_counts = df['Role'].value_counts().head(8)
    top_roles = role_counts.index.tolist()
    df_filtered_local = df[df['Role'].isin(top_roles)]
    df_filtered_local['Role_Short'] = df_filtered_local['Role'].apply(shorten_role)
    cross_tab = pd.crosstab(df_filtered_local['Role_Short'], df_filtered_local[value_col], normalize='index')*100
    role_short_order = [shorten_role(r) for r in top_roles]
    cross_tab = cross_tab.reindex(role_short_order)
    max_label_len = max([len(r) for r in cross_tab.index])
    orientation = 'h' if max_label_len > 20 else 'v'
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
            marker_color=colors[idx % len(colors)]
        ))
    fig.update_layout(
        barmode='stack',
        title=title,
        xaxis=dict(title='Percentage of Responses', range=[0,100] if orientation=='h' else None),
        yaxis=dict(title='Role' if orientation=='h' else None),
        height=max(500, 60*len(cross_tab)+150),
        margin=dict(l=200, r=50, t=100, b=150),
        legend=dict(title='Response', traceorder='normal')
    )
    return fig

st.plotly_chart(create_stacked_bar(df, 'Work_Fulfillment', 'Work Fulfillment Distribution by Role'), use_container_width=True)
st.plotly_chart(create_stacked_bar(df, 'Recognition', 'Recognition Distribution by Role'), use_container_width=True)
st.plotly_chart(create_stacked_bar(df, 'Growth_Potential', 'Growth Potential Distribution by Role'), use_container_width=True)

# 🔹 Stacked Bar Insights
role_scores = df_insights.groupby('Role')['Recommendation_Score'].mean().sort_values()
extreme_roles = df_insights[df_insights['Work_Fulfillment'].str.contains('extremely', case=False, na=False)]['Role_Short'].unique()
st.markdown("### 📝 Final Insights & Recommendations")
if len(extreme_roles) > 0:
    st.markdown("- Roles with highest 'Extremely Fulfilling' responses: " + ", ".join(extreme_roles[:5]))
if len(role_scores) >= 3:
    low_roles = [shorten_role(r) for r in role_scores.head(3).index]
    st.markdown("- Roles with lowest recommendation scores: " + ", ".join(low_roles))
st.markdown("- Consider targeted interventions for roles with consistently low scores in Work Fulfillment, Recognition, or Growth Potential.")
