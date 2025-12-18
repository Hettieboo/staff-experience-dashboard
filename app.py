import streamlit as st 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(page_title="Survey Cross-Analysis", page_icon="📊", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main {padding: 0rem 1rem;}
    h1 {color: #2c3e50; padding-bottom: 10px;}
    h2 {color: #34495e; padding-top: 15px; padding-bottom: 10px;}
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel('Combined- Cross Analysis.xlsx')
    df.columns = ['Role', 'Ethnicity', 'Disability', 'Work_Fulfillment', 'Recommendation_Score', 'Recognition', 'Growth_Potential']
    return df

try:
    df = load_data()
    
    # Header
    st.title("📊 Employee Survey Cross-Analysis Dashboard")
    st.markdown("### Comparing Employee Groups Across Survey Questions")
    
    # Sidebar filters
    st.sidebar.header("🔍 Filter Data")
    roles = ['All'] + sorted(df['Role'].unique().tolist())
    selected_role = st.sidebar.selectbox("Role/Department", roles)
    
    ethnicities = ['All'] + sorted(df['Ethnicity'].unique().tolist())
    selected_ethnicity = st.sidebar.selectbox("Ethnicity", ethnicities)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_role != 'All':
        filtered_df = filtered_df[filtered_df['Role'] == selected_role]
    if selected_ethnicity != 'All':
        filtered_df = filtered_df[filtered_df['Ethnicity'] == selected_ethnicity]
    
    total = len(filtered_df)
    
    # Key Metrics - Beautiful Cards
    st.markdown("""
        <style>
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .metric-card-green {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }
        .metric-card-blue {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        .metric-card-orange {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 0.9em;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Responses</div>
                <div class="metric-value">{total}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_score = filtered_df['Recommendation_Score'].mean()
        st.markdown(f"""
            <div class="metric-card metric-card-blue">
                <div class="metric-label">Avg Recommendation</div>
                <div class="metric-value">{avg_score:.1f}/10</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        promoters = len(filtered_df[filtered_df['Recommendation_Score'] >= 9])
        nps = ((promoters - len(filtered_df[filtered_df['Recommendation_Score'] <= 6])) / total * 100) if total > 0 else 0
        nps_color = "metric-card-green" if nps > 20 else "metric-card-orange" if nps > 0 else "metric-card"
        st.markdown(f"""
            <div class="metric-card {nps_color}">
                <div class="metric-label">NPS Score</div>
                <div class="metric-value">{nps:.0f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        fulfilled = len(filtered_df[filtered_df['Work_Fulfillment'].str.contains('extremely', case=False, na=False)])
        pct = (fulfilled/total*100) if total > 0 else 0
        st.markdown(f"""
            <div class="metric-card metric-card-green">
                <div class="metric-label">Highly Fulfilled</div>
                <div class="metric-value">{pct:.0f}%</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # === SECTION 1: Recommendation Score by Employee Groups ===
    st.markdown("## 🎯 Recommendation Score Across Groups")
    
    col1, col2 = st.columns(2)
    
    with col1:
        role_avg = df.groupby('Role')['Recommendation_Score'].agg(['mean', 'count']).reset_index()
        role_avg = role_avg[role_avg['count'] >= 3].nlargest(10, 'mean')
        role_avg['Role_Short'] = role_avg['Role'].str[:35]
        
        fig1 = px.bar(role_avg, y='Role_Short', x='mean', orientation='h',
                     color='mean', color_continuous_scale='RdYlGn',
                     range_color=[0, 10], text='mean',
                     title="Average Score by Role (Top 10)")
        fig1.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig1.update_layout(xaxis_range=[0, 11], xaxis_title="Avg Score", yaxis_title="", height=400, showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        eth_avg = df.groupby('Ethnicity')['Recommendation_Score'].agg(['mean', 'count']).reset_index()
        eth_avg = eth_avg[eth_avg['count'] >= 3].nlargest(10, 'mean')
        eth_short = {'South Asian (including Bangladeshi, Pakistani, Indian, Sri Lankan, Indo-Caribbean, Indo-African, Indo-Fijian, West Indian)': 'South Asian',
                    'Black (including East African, West African, Central African)': 'Black (African)',
                    'Black (including Caribbean, European, American, Canadian, South American)': 'Black (Caribbean/Am)',
                    'White (including European, American, South African, Canadian)': 'White',
                    'Middle Eastern (including Arab, Afghani, Armenian, Iranian, Iraqi, Jordanian, Lebanese, Palestinian, Syrian, Yemeni)': 'Middle Eastern'}
        eth_avg['Ethnicity_Short'] = eth_avg['Ethnicity'].map(lambda x: eth_short.get(x, x[:30]))
        
        fig2 = px.bar(eth_avg, y='Ethnicity_Short', x='mean', orientation='h',
                     color='mean', color_continuous_scale='RdYlGn',
                     range_color=[0, 10], text='mean',
                     title="Average Score by Ethnicity (Top 10)")
        fig2.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig2.update_layout(xaxis_range=[0, 11], xaxis_title="Avg Score", yaxis_title="", height=400, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("---")
    
    # === SECTION 2: Work Fulfillment by Groups ===
    st.markdown("## 💼 Work Fulfillment Across Groups")
    
    top_roles = df['Role'].value_counts().head(8).index
    role_fulfill = df[df['Role'].isin(top_roles)]
    fulfill_cross = pd.crosstab(role_fulfill['Role'], 
                                role_fulfill['Work_Fulfillment'].str[:30], 
                                normalize='index') * 100
    
    fig3 = go.Figure()
    colors = ['#1a9850', '#91cf60', '#fee08b', '#fc8d59', '#d73027']
    for i, col in enumerate(fulfill_cross.columns):
        fig3.add_trace(go.Bar(
            y=[r[:35] for r in fulfill_cross.index],
            x=fulfill_cross[col],
            name=col,
            orientation='h',
            marker_color=colors[i % len(colors)],
            text=[f'{v:.0f}%' if v > 8 else '' for v in fulfill_cross[col]],
            textposition='inside'
        ))
    
    fig3.update_layout(
        barmode='stack',
        title="Work Fulfillment Distribution by Role (%)",
        xaxis_title="Percentage", yaxis_title="",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("---")
    
    # === SECTION 3: Improved Recognition & Growth Sentiment Across Groups ===
    st.markdown("## 🌟 Recognition & Growth Sentiment Across Groups")
    
    # Prepare Recognition data
    recog_map = {
        'Yes, I do feel recognized and acknowledged': 'Yes',
        'I somewhat feel recognized and acknowledged': 'Somewhat',
        'I do find myself being recognized and acknowledged, but it\'s rare given the contributions I make': 'Rare',
        'I don\'t feel recognized and acknowledged and would prefer staff successes to be highlighted more frequently': 'No (Want More)',
        'I don\'t feel recognized and acknowledged but I prefer it that way': 'No (Prefer)'
    }
    df_recog = df.copy()
    df_recog['Recognition_Short'] = df_recog['Recognition'].map(recog_map)
    role_recog = df_recog[df_recog['Role'].isin(top_roles)]
    recog_cross = pd.crosstab(role_recog['Role'], role_recog['Recognition_Short'], normalize='index') * 100
    
    # Prepare Growth data
    growth_map = {
        'Yes, I do feel there is potential to grow and I hope to advance my career with Homes First': 'Yes',
        'There is some potential to grow and I hope to advance my career with Homes First': 'Some',
        'Potential to grow seems limited at Homes First and I will likely need to advance my career with another organization': 'Limited',
        'There is very little potential to grow although I would like to advance my career with Homes First': 'Very Limited',
        'I am not interested in career growth and prefer to remain in my current role': 'Not Interested'
    }
    df_growth = df.copy()
    df_growth['Growth_Short'] = df_growth['Growth_Potential'].map(growth_map)
    role_growth = df_growth[df_growth['Role'].isin(top_roles)]
    growth_cross = pd.crosstab(role_growth['Role'], role_growth['Growth_Short'], normalize='index') * 100
    
    # Sort roles by positive sentiment
    if 'Yes' in recog_cross.columns:
        recog_cross = recog_cross.sort_values('Yes', ascending=False)
        growth_cross = growth_cross.reindex(recog_cross.index)
    
    recog_order = ['Yes', 'Somewhat', 'Rare', 'No (Want More)', 'No (Prefer)']
    growth_order = ['Yes', 'Some', 'Limited', 'Very Limited', 'Not Interested']
    recog_cross = recog_cross[[c for c in recog_order if c in recog_cross.columns]]
    growth_cross = growth_cross[[c for c in growth_order if c in growth_cross.columns]]
    
    colors = ['#1a9850', '#91cf60', '#fee08b', '#fc8d59', '#d73027']
    
    fig = go.Figure()
    for i, col in enumerate(recog_cross.columns):
        fig.add_trace(go.Bar(
            y=[r[:35] for r in recog_cross.index],
            x=recog_cross[col],
            name=f"Recognition: {col}",
            orientation='h',
            marker_color=colors[i % len(colors)],
            text=[f'{v:.0f}%' for v in recog_cross[col]],
            textposition='inside'
        ))
    for i, col in enumerate(growth_cross.columns):
        fig.add_trace(go.Bar(
            y=[r[:35] for r in growth_cross.index],
            x=growth_cross[col],
            name=f"Growth: {col}",
            orientation='h',
            marker_color=colors[i % len(colors)],
            text=[f'{v:.0f}%' for v in growth_cross[col]],
            textposition='inside',
            marker=dict(line=dict(color='black', width=1), pattern=dict(shape='/'))
        ))
    
    fig.update_layout(
        barmode='stack',
        title="Recognition & Growth Sentiment by Role (%)",
        xaxis_title="Percentage",
        yaxis_title="",
        height=60 + len(recog_cross.index)*40,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # === SECTIONS 4 & 5 and sidebar as original ===
    # You can leave your existing code for those sections here unchanged
    
except FileNotFoundError:
    st.error("❌ File not found: 'Combined- Cross Analysis.xlsx'")
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
