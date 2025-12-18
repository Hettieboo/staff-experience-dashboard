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
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Responses", total)
    with col2:
        avg_score = filtered_df['Recommendation_Score'].mean()
        st.metric("Avg Recommendation", f"{avg_score:.1f}/10")
    with col3:
        promoters = len(filtered_df[filtered_df['Recommendation_Score'] >= 9])
        nps = ((promoters - len(filtered_df[filtered_df['Recommendation_Score'] <= 6])) / total * 100) if total > 0 else 0
        st.metric("NPS Score", f"{nps:.0f}")
    with col4:
        fulfilled = len(filtered_df[filtered_df['Work_Fulfillment'].str.contains('extremely', case=False, na=False)])
        st.metric("Highly Fulfilled", f"{fulfilled/total*100:.0f}%" if total > 0 else "0%")
    
    st.markdown("---")
    
    # === SECTION 1: Recommendation Score by Employee Groups ===
    st.markdown("## 🎯 Recommendation Score Across Groups")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # By Role (Top 10)
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
        # By Ethnicity
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
    
    # Get top roles
    top_roles = df['Role'].value_counts().head(8).index
    role_fulfill = df[df['Role'].isin(top_roles)]
    
    # Create percentage crosstab
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
    
    # === SECTION 3: Recognition Across Groups ===
    st.markdown("## 🌟 Recognition Sentiment Across Groups")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Recognition by Role - DIVERGING
        recog_map = {'Yes, I do feel recognized and acknowledged': 'Yes',
                    'I somewhat feel recognized and acknowledged': 'Somewhat',
                    'I do find myself being recognized and acknowledged, but it\'s rare given the contributions I make': 'Rare',
                    'I don\'t feel recognized and acknowledged and would prefer staff successes to be highlighted more frequently': 'No (Want More)',
                    'I don\'t feel recognized and acknowledged but I prefer it that way': 'No (Prefer)'}
        
        df_recog = df.copy()
        df_recog['Recognition_Short'] = df_recog['Recognition'].map(recog_map)
        
        role_recog = df_recog[df_recog['Role'].isin(top_roles)]
        recog_cross = pd.crosstab(role_recog['Role'], role_recog['Recognition_Short'], normalize='index') * 100
        
        # Calculate positive and negative
        positive_cols = ['Yes', 'Somewhat']
        negative_cols = ['Rare', 'No (Want More)', 'No (Prefer)']
        
        fig4 = go.Figure()
        
        # Negative (left side)
        for col in negative_cols:
            if col in recog_cross.columns:
                color = '#e74c3c' if 'No' in col else '#e67e22'
                fig4.add_trace(go.Bar(
                    y=[r[:30] for r in recog_cross.index],
                    x=-recog_cross[col],
                    name=col,
                    orientation='h',
                    marker_color=color,
                    text=[f'{v:.0f}%' if v > 5 else '' for v in recog_cross[col]],
                    textposition='inside',
                    hovertemplate='<b>%{y}</b><br>' + col + ': %{text}<extra></extra>',
                    customdata=recog_cross[col]
                ))
        
        # Positive (right side)
        for col in positive_cols:
            if col in recog_cross.columns:
                color = '#27ae60' if col == 'Yes' else '#52c77a'
                fig4.add_trace(go.Bar(
                    y=[r[:30] for r in recog_cross.index],
                    x=recog_cross[col],
                    name=col,
                    orientation='h',
                    marker_color=color,
                    text=[f'{v:.0f}%' if v > 5 else '' for v in recog_cross[col]],
                    textposition='inside'
                ))
        
        fig4.update_layout(
            barmode='relative',
            title="Recognition by Role (%) - Negative ← → Positive",
            xaxis_title="← Negative   |   Positive →",
            yaxis_title="",
            height=450,
            xaxis=dict(range=[-100, 100], tickvals=[-100, -50, 0, 50, 100], 
                      ticktext=['100%', '50%', '0', '50%', '100%']),
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="right", x=1.15)
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    with col2:
        # Growth Potential by Role - DIVERGING
        growth_map = {'Yes, I do feel there is potential to grow and I hope to advance my career with Homes First': 'Yes',
                     'There is some potential to grow and I hope to advance my career with Homes First': 'Some',
                     'Potential to grow seems limited at Homes First and I will likely need to advance my career with another organization': 'Limited',
                     'There is very little potential to grow although I would like to advance my career with Homes First': 'Very Limited',
                     'I am not interested in career growth and prefer to remain in my current role': 'Not Interested'}
        
        df_growth = df.copy()
        df_growth['Growth_Short'] = df_growth['Growth_Potential'].map(growth_map)
        
        role_growth = df_growth[df_growth['Role'].isin(top_roles)]
        growth_cross = pd.crosstab(role_growth['Role'], role_growth['Growth_Short'], normalize='index') * 100
        
        fig5 = go.Figure()
        
        positive_growth = ['Yes', 'Some']
        negative_growth = ['Limited', 'Very Limited', 'Not Interested']
        
        # Negative (left)
        for col in negative_growth:
            if col in growth_cross.columns:
                color = '#e74c3c' if 'Very Limited' in col else '#e67e22' if 'Limited' in col else '#95a5a6'
                fig5.add_trace(go.Bar(
                    y=[r[:30] for r in growth_cross.index],
                    x=-growth_cross[col],
                    name=col,
                    orientation='h',
                    marker_color=color,
                    text=[f'{v:.0f}%' if v > 5 else '' for v in growth_cross[col]],
                    textposition='inside'
                ))
        
        # Positive (right)
        for col in positive_growth:
            if col in growth_cross.columns:
                color = '#27ae60' if col == 'Yes' else '#52c77a'
                fig5.add_trace(go.Bar(
                    y=[r[:30] for r in growth_cross.index],
                    x=growth_cross[col],
                    name=col,
                    orientation='h',
                    marker_color=color,
                    text=[f'{v:.0f}%' if v > 5 else '' for v in growth_cross[col]],
                    textposition='inside'
                ))
        
        fig5.update_layout(
            barmode='relative',
            title="Growth Potential by Role (%) - Negative ← → Positive",
            xaxis_title="← Negative   |   Positive →",
            yaxis_title="",
            height=450,
            xaxis=dict(range=[-100, 100], tickvals=[-100, -50, 0, 50, 100],
                      ticktext=['100%', '50%', '0', '50%', '100%']),
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="right", x=1.15)
        )
        st.plotly_chart(fig5, use_container_width=True)
    
    st.markdown("---")
    
    # === SECTION 4: Heatmap - Role vs Recognition Impact on Score ===
    st.markdown("## 🔥 Cross-Analysis: How Role + Recognition Affect Scores")
    
    cross_data = df[df['Role'].isin(top_roles)].copy()
    cross_data['Role_Short'] = cross_data['Role'].str[:30]
    cross_data['Recognition_Short'] = cross_data['Recognition'].map(recog_map)
    
    pivot = cross_data.pivot_table(values='Recommendation_Score', 
                                   index='Role_Short', 
                                   columns='Recognition_Short', 
                                   aggfunc='mean')
    
    fig6 = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='RdYlGn',
        zmid=5, zmin=0, zmax=10,
        text=[[f'{v:.1f}' if not pd.isna(v) else '' for v in row] for row in pivot.values],
        texttemplate='%{text}',
        textfont={"size": 11},
        colorbar=dict(title="Score")
    ))
    
    fig6.update_layout(
        title="Average Recommendation Score: Role × Recognition Level",
        xaxis_title="Recognition Level", yaxis_title="Role",
        height=500
    )
    st.plotly_chart(fig6, use_container_width=True)
    
    st.markdown("---")
    
    # === SECTION 5: Disability Analysis ===
    st.markdown("## ♿ Disability Status Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Disability distribution - Better donut
        dis_counts = df['Disability'].value_counts().head(6)
        dis_map = {'I do not identify as an individual living with a disability/disabilities.': 'No Disability',
                  'I do identify as an individual living with a disability/disabilities but I prefer not to specify the type of disability/disabilities': 'Yes (Not Specified)',
                  'Mental health related': 'Mental Health',
                  'Mobility': 'Mobility',
                  'Other (Please specify in text box)': 'Other',
                  'Seeing': 'Seeing'}
        dis_labels = [dis_map.get(x, x[:20]) for x in dis_counts.index]
        
        fig7 = go.Figure(go.Pie(
            labels=dis_labels,
            values=dis_counts.values,
            hole=0.4,
            marker=dict(colors=px.colors.sequential.Purples),
            textposition='outside',
            textinfo='label+percent',
            textfont=dict(size=11)
        ))
        fig7.update_layout(
            title="Disability Status Distribution",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig7, use_container_width=True)
    
    with col2:
        # Score by disability - RED to GREEN scale
        dis_avg = df.groupby('Disability')['Recommendation_Score'].agg(['mean', 'count']).reset_index()
        dis_avg = dis_avg[dis_avg['count'] >= 3].sort_values('mean', ascending=True).head(8)
        dis_avg['Disability_Short'] = dis_avg['Disability'].apply(lambda x: dis_map.get(x, x[:20]))
        
        # Create color mapping based on score (red=low, yellow=mid, green=high)
        colors_dis = []
        for score in dis_avg['mean']:
            if score < 4:
                colors_dis.append('#d73027')  # Red
            elif score < 6:
                colors_dis.append('#fc8d59')  # Orange
            elif score < 7:
                colors_dis.append('#fee08b')  # Yellow
            elif score < 8:
                colors_dis.append('#d9ef8b')  # Light green
            else:
                colors_dis.append('#91cf60')  # Green
        
        fig8 = go.Figure(go.Bar(
            y=dis_avg['Disability_Short'],
            x=dis_avg['mean'],
            orientation='h',
            marker=dict(color=colors_dis),
            text=[f'{score:.1f}' for score in dis_avg['mean']],
            textposition='outside'
        ))
        
        fig8.update_layout(
            title="Avg Recommendation Score by Disability Status",
            xaxis_title="Avg Score",
            yaxis_title="",
            xaxis=dict(range=[0, 11]),
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig8, use_container_width=True)
    
    # Add insight text
    no_dis_score = df[df['Disability'].str.contains('do not identify', na=False)]['Recommendation_Score'].mean()
    mental_health_score = df[df['Disability'].str.contains('Mental health', na=False)]['Recommendation_Score'].mean()
    
    if not pd.isna(mental_health_score) and not pd.isna(no_dis_score):
        diff = no_dis_score - mental_health_score
        st.info(f"💡 **Insight:** Employees with mental health disabilities report lower satisfaction ({mental_health_score:.1f}/10) compared to those without disabilities ({no_dis_score:.1f}/10) — a difference of {diff:.1f} points.")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Cross-Analysis Dashboard v1.0**")

except FileNotFoundError:
    st.error("❌ File not found: 'Combined- Cross Analysis.xlsx'")
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
