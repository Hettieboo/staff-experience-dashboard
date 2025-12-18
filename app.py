import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Staff Experience Cross Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Staff Experience & Job Fulfillment – Cross Analysis")
st.markdown(
    """
    This dashboard examines whether demographic and organizational factors
    influence **job fulfillment and staff experience** at Homes First.
    """
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("Combined- Cross Analysis.xlsx")
    df = df.fillna("No response")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ Data file not found. Please ensure 'Combined- Cross Analysis.xlsx' is in the correct directory.")
    st.stop()

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.facecolor'] = 'white'

# --------------------------------------------------
# COLUMN DEFINITIONS
# --------------------------------------------------
role_col = "Select the role/department that best describes your current position at Homes First."
race_col = "Which racial or ethnic identity/identities best reflect you. (Select all that apply.)"
disability_col = "Do you identify as an individual living with a disabili... disability/disabilities do you have? (Select all that apply.)"

fulfillment_col = "How fulfilling and rewarding do you find your work?"
recommend_col = "How likely are you to recommend Homes First as a good place to work?"
recognition_col = "Do you feel you get acknowledged and recognized for your contribution  at work?"
growth_col = "Do you feel there is potential for growth at Homes First?"

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("🔍 Filters")

# Role filter
roles = ["All"] + sorted([r for r in df[role_col].unique() if r != "No response"])
selected_role = st.sidebar.selectbox("Filter by Role/Department", roles)

# Apply filters
filtered_df = df.copy()
if selected_role != "All":
    filtered_df = filtered_df[filtered_df[role_col] == selected_role]

st.sidebar.metric("Filtered Responses", len(filtered_df))

if len(filtered_df) == 0:
    st.warning("⚠️ No data available for the selected filters.")
    st.stop()

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------
st.header("📈 Key Staff Experience Indicators")

total_responses = len(filtered_df)

high_fulfillment = (
    filtered_df[fulfillment_col]
    .astype(str)
    .str.contains("Very|Extremely", case=False, na=False)
    .sum()
)

recommend_positive = (
    filtered_df[recommend_col]
    .astype(str)
    .str.contains("Very|Extremely|Likely", case=False, na=False)
    .sum()
)

growth_positive = (
    filtered_df[growth_col]
    .astype(str)
    .str.contains("Yes", case=False, na=False)
    .sum()
)

recognition_positive = (
    filtered_df[recognition_col]
    .astype(str)
    .str.contains("Yes", case=False, na=False)
    .sum()
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "📋 Total Responses", 
    total_responses
)

col2.metric(
    "😊 High Job Fulfillment",
    f"{high_fulfillment / total_responses:.0%}",
    delta=f"{high_fulfillment} respondents"
)

col3.metric(
    "👍 Would Recommend",
    f"{recommend_positive / total_responses:.0%}",
    delta=f"{recommend_positive} respondents"
)

col4.metric(
    "📈 See Growth Potential",
    f"{growth_positive / total_responses:.0%}",
    delta=f"{growth_positive} respondents"
)

# --------------------------------------------------
# CROSS-ANALYSIS FUNCTION WITH IMPROVED CHARTS
# --------------------------------------------------
def cross_analysis_enhanced(factor_col, title, df_data):
    st.subheader(title)
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Visualization", "📈 Breakdown Table", "🎯 Satisfaction Score"])
    
    with tab1:
        # Calculate cross-tabulation
        cross_tab = pd.crosstab(
            df_data[factor_col].astype(str),
            df_data[fulfillment_col].astype(str),
            normalize="index"
        ) * 100
        
        # Create stacked bar chart
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Use a color palette
        colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(cross_tab.columns)))
        
        cross_tab.plot(kind="bar", stacked=True, ax=ax, color=colors, width=0.7)
        
        ax.set_ylabel("Percentage (%)", fontsize=12, fontweight='bold')
        ax.set_xlabel("")
        ax.set_title("Distribution of Job Fulfillment", fontsize=14, fontweight='bold', pad=20)
        ax.legend(title="Fulfillment Level", bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.set_ylim(0, 100)
        
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        
        st.pyplot(fig)
        plt.close()
    
    with tab2:
        # Show detailed breakdown
        cross_tab_display = cross_tab.round(1)
        cross_tab_display['Total Responses'] = df_data.groupby(factor_col).size()
        
        # Style the dataframe
        styled_df = cross_tab_display.style.background_gradient(
            cmap='RdYlGn', 
            subset=cross_tab_display.columns[:-1],
            vmin=0, 
            vmax=100
        ).format("{:.1f}%", subset=cross_tab_display.columns[:-1])
        
        st.dataframe(styled_df, use_container_width=True)
    
    with tab3:
        # Calculate satisfaction scores
        satisfaction_map = {
            'Extremely fulfilling': 5,
            'Very fulfilling': 4,
            'Moderately fulfilling': 3,
            'Slightly fulfilling': 2,
            'Not at all fulfilling': 1
        }
        
        temp_df = df_data.copy()
        temp_df['score'] = temp_df[fulfillment_col].astype(str).map(satisfaction_map)
        
        avg_scores = temp_df.groupby(factor_col)['score'].agg(['mean', 'count']).reset_index()
        avg_scores.columns = ['Category', 'Avg Score', 'Count']
        avg_scores = avg_scores.sort_values('Avg Score', ascending=False)
        
        # Create horizontal bar chart
        fig, ax = plt.subplots(figsize=(10, max(6, len(avg_scores) * 0.5)))
        
        colors_map = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(avg_scores)))
        bars = ax.barh(avg_scores['Category'], avg_scores['Avg Score'], color=colors_map)
        
        # Add value labels
        for i, (score, count) in enumerate(zip(avg_scores['Avg Score'], avg_scores['Count'])):
            ax.text(score + 0.1, i, f'{score:.2f} (n={count})', 
                   va='center', fontsize=10, fontweight='bold')
        
        ax.set_xlabel('Average Satisfaction Score', fontsize=12, fontweight='bold')
        ax.set_ylabel('')
        ax.set_title('Average Satisfaction Score (1-5 scale)', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlim(0, 5.5)
        ax.axvline(x=3, color='gray', linestyle='--', alpha=0.5, linewidth=1)
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

# --------------------------------------------------
# CROSS-ANALYSIS SECTIONS
# --------------------------------------------------
st.header("🔄 Cross Analysis Results")

cross_analysis_enhanced(role_col, "Job Fulfillment by Role / Department", filtered_df)
st.divider()
cross_analysis_enhanced(race_col, "Job Fulfillment by Race / Ethnicity", filtered_df)
st.divider()
cross_analysis_enhanced(disability_col, "Job Fulfillment by Disability Status", filtered_df)

# --------------------------------------------------
# EXPERIENCE DRIVERS
# --------------------------------------------------
st.header("🎯 Key Drivers of Staff Experience")

driver_map = {
    "Recognition at Work": recognition_col,
    "Growth Opportunities": growth_col,
    "Likelihood to Recommend": recommend_col,
}

cols = st.columns(3)

for idx, (label, col) in enumerate(driver_map.items()):
    with cols[idx]:
        st.subheader(label)
        
        breakdown = (
            filtered_df[col]
            .astype(str)
            .value_counts(normalize=True) * 100
        ).round(1)
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=(8, 8))
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(breakdown)))
        wedges, texts, autotexts = ax.pie(
            breakdown.values, 
            labels=breakdown.index,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            textprops={'fontsize': 10}
        )
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title(f"{label}\nDistribution", fontsize=12, fontweight='bold', pad=20)
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

# --------------------------------------------------
# CORRELATION HEATMAP
# --------------------------------------------------
st.header("🔗 Experience Factor Correlations")

# Create a simplified correlation matrix
binary_cols = {
    'High Fulfillment': filtered_df[fulfillment_col].astype(str).str.contains("Very|Extremely", case=False, na=False).astype(int),
    'Would Recommend': filtered_df[recommend_col].astype(str).str.contains("Very|Extremely|Likely", case=False, na=False).astype(int),
    'Recognized': filtered_df[recognition_col].astype(str).str.contains("Yes", case=False, na=False).astype(int),
    'Growth Potential': filtered_df[growth_col].astype(str).str.contains("Yes", case=False, na=False).astype(int),
}

corr_df = pd.DataFrame(binary_cols)
correlation_matrix = corr_df.corr()

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(
    correlation_matrix, 
    annot=True, 
    fmt='.2f', 
    cmap='RdYlGn',
    center=0,
    vmin=-1,
    vmax=1,
    square=True,
    linewidths=1,
    cbar_kws={"shrink": 0.8},
    ax=ax
)
ax.set_title('Correlation Between Experience Factors', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
st.pyplot(fig)
plt.close()

# --------------------------------------------------
# INSIGHTS & RECOMMENDATIONS
# --------------------------------------------------
st.header("💡 Insights & Recommendations")

insight_tab, rec_tab = st.tabs(["Key Insights", "Recommendations"])

with insight_tab:
    st.markdown("""
    ### 🔍 Key Insights
    
    - **Role Variation**: Job fulfillment varies significantly across roles and departments,
      suggesting operational context strongly shapes staff experience.
      
    - **Growth Connection**: Perceived career growth opportunities are closely linked to
      higher fulfillment and stronger advocacy for the organization.
      
    - **Equity Gaps**: Differences across race, ethnicity, and disability status
      indicate uneven staff experiences that may reflect systemic or
      accessibility-related factors.
      
    - **Recognition Impact**: Recognition and acknowledgment consistently emerge as
      strong drivers of positive sentiment.
    """)

with rec_tab:
    st.markdown("""
    ### 🎯 Recommendations
    
    **1. Role-Specific Engagement Strategies**  
    Target roles with lower fulfillment for workload review, management support,
    and tailored engagement initiatives.
    
    **2. Strengthen Career Pathways**  
    Clearly communicate advancement opportunities, professional development
    options, and internal mobility pathways.
    
    **3. Formalize Recognition Mechanisms**  
    Introduce consistent, organization-wide recognition practices to ensure
    visibility of staff contributions.
    
    **4. Deepen Equity & Inclusion Efforts**  
    Conduct qualitative follow-ups with under-represented groups to identify
    barriers impacting experience and fulfillment.
    
    **5. Monitor Progress Over Time**  
    Use this dashboard longitudinally to assess whether interventions lead to
    measurable improvements in staff experience.
    """)

# --------------------------------------------------
# EXPORT OPTIONS
# --------------------------------------------------
st.header("📥 Export Data")

col1, col2 = st.columns(2)

with col1:
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📄 Download Filtered Data as CSV",
        data=csv,
        file_name="staff_experience_filtered.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    st.info("💡 Tip: Use filters in the sidebar to refine your analysis before exporting.")

st.divider()
st.caption("📊 This analysis supports evidence-based people and culture decision-making.")
