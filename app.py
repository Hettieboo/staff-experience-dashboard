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

def shorten_text(text, max_length=30):
    return text if len(text) <= max_length else text[:max_length-3] + '...'

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

# =================== TAB 1: BY ROLE ===================
with tab1:
    st.markdown("### Analysis by Role/Department")
    
    top_roles = df['Role'].value_counts().head(8).index.tolist()
    df_cross = df[df['Role'].isin(top_roles)].copy()
    df_cross['Role_Short'] = df_cross['Role'].apply(shorten_role)
    
    def create_diverging_bar(df, question_col, title, positive_keywords, neutral_keywords, negative_keywords):
        role_data = []
        roles = sorted(df['Role_Short'].unique())
        
        for role in roles:
            role_subset = df[df['Role_Short'] == role]
            total = len(role_subset)
            if total == 0:
                continue
            
            positive = sum(role_subset[question_col].str.contains('|'.join(positive_keywords), case=False, na=False)) / total * 100
            neutral = sum(role_subset[question_col].str.contains('|'.join(neutral_keywords), case=False, na=False)) / total * 100
            negative = sum(role_subset[question_col].str.contains('|'.join(negative_keywords), case=False, na=False)) / total * 100
            
            role_data.append({'Role': role, 'Positive': positive, 'Neutral': neutral, 'Negative': negative})
        
        df_chart = pd.DataFrame(role_data)
        fig = go.Figure()
        
        fig.add_trace(go.Bar(y=df_chart['Role'], x=-df_chart['Negative'], name='Negative', orientation='h',
            marker=dict(color='#e74c3c'), text=[f'{val:.0f}%' if val > 5 else '' for val in df_chart['Negative']],
            textposition='inside', textfont=dict(color='white', size=11)))
        
        fig.add_trace(go.Bar(y=df_chart['Role'], x=df_chart['Neutral'], name='Neutral', orientation='h',
            marker=dict(color='#f39c12'), text=[f'{val:.0f}%' if val > 5 else '' for val in df_chart['Neutral']],
            textposition='inside', textfont=dict(color='white', size=11)))
        
        fig.add_trace(go.Bar(y=df_chart['Role'], x=df_chart['Positive'], name='Positive', orientation='h',
            marker=dict(color='#27ae60'), text=[f'{val:.0f}%' if val > 5 else '' for val in df_chart['Positive']],
            textposition='inside', textfont=dict(color='white', size=11)))
        
        fig.update_layout(barmode='relative', title=dict(text=title, font=dict(size=16, color='#2c3e50')),
            xaxis=dict(title='← Negative    |    Positive →', range=[-100, 100],
                tickvals=[-100, -75, -50, -25, 0, 25, 50, 75, 100],
                ticktext=['100%', '75%', '50%', '25%', '0', '25%', '50%', '75%', '100%'],
                showline=True, linewidth=2, linecolor='#34495e', showgrid=True, gridcolor='#ecf0f1',
                zeroline=True, zerolinewidth=3, zerolinecolor='#34495e'),
            yaxis=dict(title='Role', showline=True, linewidth=2, linecolor='#34495e', showgrid=False),
            height=500, margin=dict(l=200, r=50, t=80, b=80),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
            plot_bgcolor='white', paper_bgcolor='#f8f9fa')
        
        fig.update_xaxes(mirror=True, ticks='outside', showline=True, linecolor='#34495e', linewidth=2)
        fig.update_yaxes(mirror=True, ticks='outside', showline=True, linecolor='#34495e', linewidth=2)
        return fig
    
    st.subheader("💼 Work Fulfillment by Role")
    st.plotly_chart(create_diverging_bar(df_cross, 'Work_Fulfillment', 'Work Fulfillment Sentiment',
        ['extremely fulfilling'], ['somewhat', 'in some parts'], ["don't find the work", "taking steps to change"]), use_container_width=True)
    
    st.subheader("🌟 Recognition by Role")
    st.plotly_chart(create_diverging_bar(df_cross, 'Recognition', 'Recognition Sentiment',
        ['Yes, I do feel recognized'], ['somewhat', 'rare', 'prefer it that way'], ["don't feel recognized and would prefer"]), use_container_width=True)
    
    st.subheader("📈 Growth Potential by Role")
    st.plotly_chart(create_diverging_bar(df_cross, 'Growth_Potential', 'Growth Potential Sentiment',
        ['Yes, I do feel there is potential'], ['some potential', 'not interested in career growth'], ['limited', 'very little']), use_container_width=True)

# =================== TAB 2: BY ETHNICITY ===================
with tab2:
    st.markdown("### Analysis by Ethnicity")
    
    top_ethnicities = df['Ethnicity'].value_counts().head(8).index.tolist()
    df_eth = df[df['Ethnicity'].isin(top_ethnicities)].copy()
    df_eth['Ethnicity_Short'] = df_eth['Ethnicity'].apply(shorten_ethnicity)
    
    def create_diverging_bar_eth(df, question_col, title, positive_keywords, neutral_keywords, negative_keywords):
        eth_data = []
        ethnicities = sorted(df['Ethnicity_Short'].unique())
        
        for eth in ethnicities:
            eth_subset = df[df['Ethnicity_Short'] == eth]
            total = len(eth_subset)
            if total == 0:
                continue
            
            positive = sum(eth_subset[question_col].str.contains('|'.join(positive_keywords), case=False, na=False)) / total * 100
            neutral = sum(eth_subset[question_col].str.contains('|'.join(neutral_keywords), case=False, na=False)) / total * 100
            negative = sum(eth_subset[question_col].str.contains('|'.join(negative_keywords), case=False, na=False)) / total * 100
            
            eth_data.append({'Ethnicity': eth, 'Positive': positive, 'Neutral': neutral, 'Negative': negative})
        
        df_chart = pd.DataFrame(eth_data)
        fig = go.Figure()
        
        fig.add_trace(go.Bar(y=df_chart['Ethnicity'], x=-df_chart['Negative'], name='Negative', orientation='h',
            marker=dict(color='#e74c3c'), text=[f'{val:.0f}%' if val > 5 else '' for val in df_chart['Negative']],
            textposition='inside', textfont=dict(color='white', size=11)))
        
        fig.add_trace(go.Bar(y=df_chart['Ethnicity'], x=df_chart['Neutral'], name='Neutral', orientation='h',
            marker=dict(color='#f39c12'), text=[f'{val:.0f}%' if val > 5 else '' for val in df_chart['Neutral']],
            textposition='inside', textfont=dict(color='white', size=11)))
        
        fig.add_trace(go.Bar(y=df_chart['Ethnicity'], x=df_chart['Positive'], name='Positive', orientation='h',
            marker=dict(color='#27ae60'), text=[f'{val:.0f}%' if val > 5 else '' for val in df_chart['Positive']],
            textposition='inside', textfont=dict(color='white', size=11)))
        
        fig.update_layout(barmode='relative', title=dict(text=title, font=dict(size=16, color='#2c3e50')),
            xaxis=dict(title='← Negative    |    Positive →', range=[-100, 100],
                tickvals=[-100, -75, -50, -25, 0, 25, 50, 75, 100],
                ticktext=['100%', '75%', '50%', '25%', '0', '25%', '50%', '75%', '100%'],
                showline=True, linewidth=2, linecolor='#34495e', showgrid=True, gridcolor='#ecf0f1',
                zeroline=True, zerolinewidth=3, zerolinecolor='#34495e'),
            yaxis=dict(title='Ethnicity', showline=True, linewidth=2, linecolor='#34495e', showgrid=False),
            height=500, margin=dict(l=200, r=50, t=80, b=80),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
            plot_bgcolor='white', paper_bgcolor='#f8f9fa')
        
        fig.update_xaxes(mirror=True, ticks='outside', showline=True, linecolor='#34495e', linewidth=2)
        fig.update_yaxes(mirror=True, ticks='outside', showline=True, linecolor='#34495e', linewidth=2)
        return fig
    
    st.subheader("💼 Work Fulfillment by Ethnicity")
    st.plotly_chart(create_diverging_bar_eth(df_eth, 'Work_Fulfillment', 'Work Fulfillment Sentiment',
        ['extremely fulfilling'], ['somewhat', 'in some parts'], ["don't find the work", "taking steps to change"]), use_container_width=True)
    
    st.subheader("🌟 Recognition by Ethnicity")
    st.plotly_chart(create_diverging_bar_eth(df_eth, 'Recognition', 'Recognition Sentiment',
        ['Yes, I do feel recognized'], ['somewhat', 'rare', 'prefer it that way'], ["don't feel recognized and would prefer"]), use_container_width=True)
    
    st.subheader("📈 Growth Potential by Ethnicity")
    st.plotly_chart(create_diverging_bar_eth(df_eth, 'Growth_Potential', 'Growth Potential Sentiment',
        ['Yes, I do feel there is potential'], ['some potential', 'not interested in career growth'], ['limited', 'very little']), use_container_width=True)

# =================== TAB 3: BY DISABILITY ===================
with tab3:
    st.markdown("### Analysis by Disability Status")
    
    df_dis = df.copy()
    df_dis['Disability_Short'] = df_dis['Disability_Category']
    
    def create_diverging_bar_dis(df, question_col, title, positive_keywords, neutral_keywords, negative_keywords):
        dis_data = []
        disabilities = sorted(df['Disability_Short'].unique())
        
        for dis in disabilities:
            dis_subset = df[df['Disability_Short'] == dis]
            total = len(dis_subset)
            if total < 3:
                continue
            
            positive = sum(dis_subset[question_col].str.contains('|'.join(positive_keywords), case=False, na=False)) / total * 100
            neutral = sum(dis_subset[question_col].str.contains('|'.join(neutral_keywords), case=False, na=False)) / total * 100
            negative = sum(dis_subset[question_col].str.contains('|'.join(negative_keywords), case=False, na=False)) / total * 100
            
            dis_data.append({'Disability': dis, 'Positive': positive, 'Neutral': neutral, 'Negative': negative})
        
        df_chart = pd.DataFrame(dis_data)
        fig = go.Figure()
        
        fig.add_trace(go.Bar(y=df_chart['Disability'], x=-df_chart['Negative'], name='Negative', orientation='h',
            marker=dict(color='#e74c3c'), text=[f'{val:.0f}%' if val > 5 else '' for val in df_chart['Negative']],
            textposition='inside', textfont=dict(color='white', size=11)))
        
        fig.add_trace(go.Bar(y=df_chart['Disability'], x=df_chart['Neutral'], name='Neutral', orientation='h',
            marker=dict(color='#f39c12'), text=[f'{val:.0f}%' if val > 5 else '' for val in df_chart['Neutral']],
            textposition='inside', textfont=dict(color='white', size=11)))
        
        fig.add_trace(go.Bar(y=df_chart['Disability'], x=df_chart['Positive'], name='Positive', orientation='h',
            marker=dict(color='#27ae60'), text=[f'{val:.0f}%' if val > 5 else '' for val in df_chart['Positive']],
            textposition='inside', textfont=dict(color='white', size=11)))
        
        fig.update_layout(barmode='relative', title=dict(text=title, font=dict(size=16, color='#2c3e50')),
            xaxis=dict(title='← Negative    |    Positive →', range=[-100, 100],
                tickvals=[-100, -75, -50, -25, 0, 25, 50, 75, 100],
                ticktext=['100%', '75%', '50%', '25%', '0', '25%', '50%', '75%', '100%'],
                showline=True, linewidth=2, linecolor='#34495e', showgrid=True, gridcolor='#ecf0f1',
                zeroline=True, zerolinewidth=3, zerolinecolor='#34495e'),
            yaxis=dict(title='Disability Status', showline=True, linewidth=2, linecolor='#34495e', showgrid=False),
            height=400, margin=dict(l=200, r=50, t=80, b=80),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
            plot_bgcolor='white', paper_bgcolor='#f8f9fa')
        
        fig.update_xaxes(mirror=True, ticks='outside', showline=True, linecolor='#34495e', linewidth=2)
        fig.update_yaxes(mirror=True, ticks='outside', showline=True, linecolor='#34495e', linewidth=2)
        return fig
    
    st.subheader("💼 Work Fulfillment by Disability Status")
    st.plotly_chart(create_diverging_bar_dis(df_dis, 'Work_Fulfillment', 'Work Fulfillment Sentiment',
        ['extremely fulfilling'], ['somewhat', 'in some parts'], ["don't find the work", "taking steps to change"]), use_container_width=True)
    
    st.subheader("🌟 Recognition by Disability Status")
    st.plotly_chart(create_diverging_bar_dis(df_dis, 'Recognition', 'Recognition Sentiment',
        ['Yes, I do feel recognized'], ['somewhat', 'rare', 'prefer it that way'], ["don't feel recognized and would prefer"]), use_container_width=True)
    
    st.subheader("📈 Growth Potential by Disability Status")
    st.plotly_chart(create_diverging_bar_dis(df_dis, 'Growth_Potential', 'Growth Potential Sentiment',
        ['Yes, I do feel there is potential'], ['some potential', 'not interested in career growth'], ['limited', 'very little']), use_container_width=True)

# =================== TAB 4: HEATMAPS ===================
with tab4:
    st.markdown("### Sentiment Heatmaps")
    
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
