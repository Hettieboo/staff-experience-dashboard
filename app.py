import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Homes First Survey Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
    }
    h1 {
        color: #1f77b4;
        padding-bottom: 20px;
    }
    h2 {
        color: #2c3e50;
        padding-top: 20px;
    }
    .plot-container {
        background-color: white;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel('Combined- Cross Analysis.xlsx')
    
    # Shorten column names
    df.columns = [
        'Role',
        'Ethnicity',
        'Disability',
        'Work_Fulfillment',
        'Recommendation_Score',
        'Recognition',
        'Growth_Potential'
    ]
    
    return df

try:
    df = load_data()
    
    # Header
    st.title("📊 Homes First Employee Survey Dashboard")
    st.markdown("### Interactive Analysis of Employee Experience and Engagement")
    st.markdown("---")
    
    # Sidebar filters
    st.sidebar.header("🔍 Filter Options")
    
    # Role filter
    roles = ['All'] + sorted(df['Role'].unique().tolist())
    selected_role = st.sidebar.selectbox("Select Role/Department", roles)
    
    # Ethnicity filter
    ethnicities = ['All'] + sorted(df['Ethnicity'].unique().tolist())
    selected_ethnicity = st.sidebar.selectbox("Select Ethnicity", ethnicities)
    
    # Disability filter
    disabilities = ['All'] + sorted(df['Disability'].unique().tolist())
    selected_disability = st.sidebar.selectbox("Select Disability Status", disabilities)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_role != 'All':
        filtered_df = filtered_df[filtered_df['Role'] == selected_role]
    if selected_ethnicity != 'All':
        filtered_df = filtered_df[filtered_df['Ethnicity'] == selected_ethnicity]
    if selected_disability != 'All':
        filtered_df = filtered_df[filtered_df['Disability'] == selected_disability]
    
    # Key Metrics
    st.markdown("## 📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_responses = len(filtered_df)
        st.metric("Total Responses", total_responses)
    
    with col2:
        avg_score = filtered_df['Recommendation_Score'].mean()
        st.metric("Avg Recommendation Score", f"{avg_score:.1f}/10")
    
    with col3:
        highly_fulfilled = len(filtered_df[filtered_df['Work_Fulfillment'] == 'I find the work I do extremely fulfilling and rewarding'])
        fulfillment_pct = (highly_fulfilled / total_responses * 100) if total_responses > 0 else 0
        st.metric("Highly Fulfilled", f"{fulfillment_pct:.1f}%")
    
    with col4:
        recognized = len(filtered_df[filtered_df['Recognition'] == 'Yes, I do feel recognized and acknowledged'])
        recognition_pct = (recognized / total_responses * 100) if total_responses > 0 else 0
        st.metric("Feel Recognized", f"{recognition_pct:.1f}%")
    
    st.markdown("---")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Dashboard Version 1.0**")
    
    # OVERVIEW TAB
    if chart_type == "Overview":
        st.markdown("## 🎯 Survey Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Work Fulfillment Distribution
            fulfillment_counts = filtered_df['Work_Fulfillment'].value_counts()
            fig1 = px.pie(
                values=fulfillment_counts.values,
                names=fulfillment_counts.index,
                title="Work Fulfillment Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Recognition Distribution
            recognition_counts = filtered_df['Recognition'].value_counts()
            fig2 = px.pie(
                values=recognition_counts.values,
                names=recognition_counts.index,
                title="Recognition Sentiment Distribution",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig2.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig2, use_container_width=True)
        
        # Recommendation Score Distribution
        st.markdown("### Recommendation Score Distribution (NPS)")
        fig3 = px.histogram(
            filtered_df,
            x='Recommendation_Score',
            nbins=11,
            title="How Likely to Recommend Homes First (0-10 Scale)",
            color_discrete_sequence=['#1f77b4']
        )
        fig3.update_layout(
            xaxis_title="Recommendation Score",
            yaxis_title="Number of Responses",
            bargap=0.1
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # Growth Potential
        st.markdown("### Career Growth Potential Perception")
        growth_counts = filtered_df['Growth_Potential'].value_counts()
        fig4 = px.bar(
            x=growth_counts.index,
            y=growth_counts.values,
            title="Employee Perception of Growth Opportunities",
            color=growth_counts.values,
            color_continuous_scale='Blues'
        )
        fig4.update_layout(
            xaxis_title="Growth Perception",
            yaxis_title="Count",
            showlegend=False
        )
        fig4.update_xaxes(tickangle=-45)
        st.plotly_chart(fig4, use_container_width=True)
    
    # ROLE ANALYSIS TAB
    elif chart_type == "Role Analysis":
        st.markdown("## 👥 Role/Department Analysis")
        
        # Top roles by count
        role_counts = filtered_df['Role'].value_counts().head(10)
        fig1 = px.bar(
            x=role_counts.values,
            y=role_counts.index,
            orientation='h',
            title="Top 10 Roles by Response Count",
            color=role_counts.values,
            color_continuous_scale='Viridis'
        )
        fig1.update_layout(
            xaxis_title="Number of Responses",
            yaxis_title="Role",
            showlegend=False
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Average recommendation score by role
        st.markdown("### Average Recommendation Score by Role")
        avg_by_role = filtered_df.groupby('Role')['Recommendation_Score'].agg(['mean', 'count']).reset_index()
        avg_by_role = avg_by_role[avg_by_role['count'] >= 3].sort_values('mean', ascending=False).head(15)
        
        fig2 = px.bar(
            avg_by_role,
            x='mean',
            y='Role',
            orientation='h',
            title="Average Recommendation Score by Role (Roles with 3+ responses)",
            color='mean',
            color_continuous_scale='RdYlGn',
            range_color=[0, 10]
        )
        fig2.update_layout(
            xaxis_title="Average Score",
            yaxis_title="Role",
            showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Work fulfillment by role
        st.markdown("### Work Fulfillment by Top Roles")
        top_roles = filtered_df['Role'].value_counts().head(8).index
        role_fulfillment = filtered_df[filtered_df['Role'].isin(top_roles)]
        
        fulfillment_by_role = pd.crosstab(role_fulfillment['Role'], role_fulfillment['Work_Fulfillment'])
        fulfillment_by_role_pct = fulfillment_by_role.div(fulfillment_by_role.sum(axis=1), axis=0) * 100
        
        fig3 = px.bar(
            fulfillment_by_role_pct,
            barmode='stack',
            title="Work Fulfillment Distribution by Role (%)",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig3.update_layout(
            xaxis_title="Role",
            yaxis_title="Percentage",
            legend_title="Fulfillment Level"
        )
        fig3.update_xaxes(tickangle=-45)
        st.plotly_chart(fig3, use_container_width=True)
    
    # ETHNICITY ANALYSIS TAB
    elif chart_type == "Ethnicity Analysis":
        st.markdown("## 🌍 Ethnicity & Diversity Analysis")
        
        # Ethnicity distribution
        ethnicity_counts = filtered_df['Ethnicity'].value_counts()
        fig1 = px.bar(
            x=ethnicity_counts.index,
            y=ethnicity_counts.values,
            title="Ethnicity Distribution of Respondents",
            color=ethnicity_counts.values,
            color_continuous_scale='Teal'
        )
        fig1.update_layout(
            xaxis_title="Ethnicity",
            yaxis_title="Count",
            showlegend=False
        )
        fig1.update_xaxes(tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)
        
        # Average scores by ethnicity
        st.markdown("### Average Recommendation Score by Ethnicity")
        avg_by_ethnicity = filtered_df.groupby('Ethnicity')['Recommendation_Score'].agg(['mean', 'count']).reset_index()
        avg_by_ethnicity = avg_by_ethnicity[avg_by_ethnicity['count'] >= 3].sort_values('mean', ascending=False)
        
        fig2 = px.scatter(
            avg_by_ethnicity,
            x='mean',
            y='Ethnicity',
            size='count',
            title="Average Recommendation Score by Ethnicity (sized by response count)",
            color='mean',
            color_continuous_scale='RdYlGn',
            range_color=[0, 10]
        )
        fig2.update_layout(
            xaxis_title="Average Recommendation Score",
            yaxis_title="Ethnicity",
            xaxis_range=[0, 10]
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Recognition by ethnicity
        st.markdown("### Recognition Sentiment by Ethnicity")
        top_ethnicities = filtered_df['Ethnicity'].value_counts().head(8).index
        eth_recognition = filtered_df[filtered_df['Ethnicity'].isin(top_ethnicities)]
        
        recognition_by_eth = pd.crosstab(eth_recognition['Ethnicity'], eth_recognition['Recognition'])
        recognition_by_eth_pct = recognition_by_eth.div(recognition_by_eth.sum(axis=1), axis=0) * 100
        
        fig3 = px.bar(
            recognition_by_eth_pct,
            barmode='stack',
            title="Recognition Distribution by Ethnicity (%)",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig3.update_layout(
            xaxis_title="Ethnicity",
            yaxis_title="Percentage",
            legend_title="Recognition Level"
        )
        fig3.update_xaxes(tickangle=-45)
        st.plotly_chart(fig3, use_container_width=True)
    
    # CROSS-ANALYSIS TAB
    elif chart_type == "Cross-Analysis":
        st.markdown("## 🔄 Cross-Dimensional Analysis")
        
        # Heatmap: Recommendation Score by Role and Recognition
        st.markdown("### Recommendation Score: Role vs Recognition")
        top_roles = filtered_df['Role'].value_counts().head(10).index
        cross_data = filtered_df[filtered_df['Role'].isin(top_roles)]
        
        pivot_data = cross_data.pivot_table(
            values='Recommendation_Score',
            index='Role',
            columns='Recognition',
            aggfunc='mean'
        )
        
        fig1 = px.imshow(
            pivot_data,
            title="Average Recommendation Score: Role × Recognition",
            color_continuous_scale='RdYlGn',
            aspect='auto',
            labels=dict(color="Avg Score")
        )
        fig1.update_xaxes(side="bottom", tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)
        
        # Sunburst: Role -> Work Fulfillment -> Growth Potential
        st.markdown("### Hierarchical View: Role → Fulfillment → Growth")
        sunburst_data = filtered_df[filtered_df['Role'].isin(top_roles)].copy()
        sunburst_data['Work_Fulfillment_Short'] = sunburst_data['Work_Fulfillment'].str[:30] + '...'
        sunburst_data['Growth_Potential_Short'] = sunburst_data['Growth_Potential'].str[:30] + '...'
        
        fig2 = px.sunburst(
            sunburst_data,
            path=['Role', 'Work_Fulfillment_Short', 'Growth_Potential_Short'],
            title="Hierarchical Relationship: Role → Work Fulfillment → Growth Potential",
            color='Recommendation_Score',
            color_continuous_scale='RdYlGn',
            color_continuous_midpoint=5
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Parallel Categories
        st.markdown("### Parallel Flow: Fulfillment → Recognition → Growth")
        parallel_data = filtered_df.copy()
        parallel_data['Work_Fulfillment_Short'] = parallel_data['Work_Fulfillment'].str[:25]
        parallel_data['Recognition_Short'] = parallel_data['Recognition'].str[:25]
        parallel_data['Growth_Short'] = parallel_data['Growth_Potential'].str[:25]
        
        fig3 = px.parallel_categories(
            parallel_data,
            dimensions=['Work_Fulfillment_Short', 'Recognition_Short', 'Growth_Short'],
            color='Recommendation_Score',
            color_continuous_scale='Viridis',
            title="Flow Analysis: Fulfillment → Recognition → Growth Perception"
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    # DETAILED METRICS TAB
    elif chart_type == "Detailed Metrics":
        st.markdown("## 📊 Detailed Metrics & Insights")
        
        # Net Promoter Score Analysis
        st.markdown("### Net Promoter Score (NPS) Analysis")
        
        promoters = len(filtered_df[filtered_df['Recommendation_Score'] >= 9])
        passives = len(filtered_df[(filtered_df['Recommendation_Score'] >= 7) & (filtered_df['Recommendation_Score'] <= 8)])
        detractors = len(filtered_df[filtered_df['Recommendation_Score'] <= 6])
        total = len(filtered_df)
        
        if total > 0:
            nps = ((promoters - detractors) / total) * 100
        else:
            nps = 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Promoters (9-10)", f"{promoters} ({promoters/total*100:.1f}%)" if total > 0 else "0")
        with col2:
            st.metric("Passives (7-8)", f"{passives} ({passives/total*100:.1f}%)" if total > 0 else "0")
        with col3:
            st.metric("Detractors (0-6)", f"{detractors} ({detractors/total*100:.1f}%)" if total > 0 else "0")
        with col4:
            st.metric("NPS Score", f"{nps:.1f}")
        
        # NPS visualization
        nps_data = pd.DataFrame({
            'Category': ['Promoters', 'Passives', 'Detractors'],
            'Count': [promoters, passives, detractors],
            'Percentage': [promoters/total*100 if total > 0 else 0, 
                          passives/total*100 if total > 0 else 0, 
                          detractors/total*100 if total > 0 else 0]
        })
        
        fig1 = px.bar(
            nps_data,
            x='Category',
            y='Count',
            title="NPS Category Breakdown",
            color='Category',
            color_discrete_map={'Promoters': '#28a745', 'Passives': '#ffc107', 'Detractors': '#dc3545'},
            text='Count'
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Disability analysis
        st.markdown("### Disability Status Analysis")
        disability_counts = filtered_df['Disability'].value_counts()
        
        fig2 = px.bar(
            x=disability_counts.index,
            y=disability_counts.values,
            title="Distribution by Disability Status",
            color=disability_counts.values,
            color_continuous_scale='Blues'
        )
        fig2.update_layout(showlegend=False)
        fig2.update_xaxes(tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)
        
        # Correlation matrix
        st.markdown("### Recommendation Score Insights")
        
        # Box plot by different dimensions
        fig3 = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Score by Work Fulfillment", "Score by Recognition")
        )
        
        # Work Fulfillment
        for fulfillment in filtered_df['Work_Fulfillment'].unique():
            data = filtered_df[filtered_df['Work_Fulfillment'] == fulfillment]['Recommendation_Score']
            fig3.add_trace(
                go.Box(y=data, name=fulfillment[:20], showlegend=False),
                row=1, col=1
            )
        
        # Recognition
        for recognition in filtered_df['Recognition'].unique():
            data = filtered_df[filtered_df['Recognition'] == recognition]['Recommendation_Score']
            fig3.add_trace(
                go.Box(y=data, name=recognition[:20], showlegend=False),
                row=1, col=2
            )
        
        fig3.update_yaxes(title_text="Recommendation Score", row=1, col=1)
        fig3.update_yaxes(title_text="Recommendation Score", row=1, col=2)
        fig3.update_layout(height=500, title_text="Score Distribution Analysis")
        st.plotly_chart(fig3, use_container_width=True)
        
        # Summary statistics table
        st.markdown("### Summary Statistics")
        summary_stats = filtered_df['Recommendation_Score'].describe()
        st.dataframe(summary_stats.to_frame().T, use_container_width=True)
    
    # Data table at the bottom
    st.markdown("---")
    st.markdown("## 📋 Filtered Data Preview")
    st.dataframe(filtered_df, use_container_width=True)
    
    # Download button
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name='filtered_survey_data.csv',
        mime='text/csv',
    )

except FileNotFoundError:
    st.error("❌ Error: 'Combined- Cross Analysis.xlsx' file not found. Please ensure the file is in the same directory as this script.")
except Exception as e:
    st.error(f"❌ An error occurred: {str(e)}")
    st.info("Please check your data file format and try again.")
