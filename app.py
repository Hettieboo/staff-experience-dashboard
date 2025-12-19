import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Page config
st.set_page_config(page_title="Homes First Survey Dashboard", layout="wide")

# Custom CSS (ADDED CROSS-ANALYSIS STYLES)
st.markdown("""
<style>
    .main-title { font-size: 2.5rem; font-weight: bold; color: #1f77b4; text-align: center; margin-bottom: 2rem; }
    .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 1rem; }
    .metric-value { font-size: 2.5rem; font-weight: bold; }
    .metric-label { font-size: 1rem; opacity: 0.9; }
    .insight-card { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #fff; }
    .insight-positive { background: linear-gradient(135deg, #a8e6cf 0%, #88d8a3 100%); }
    .insight-negative { background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel('Combined- Cross Analysis.xlsx')
    df.columns = ['Role', 'Ethnicity', 'Disability', 'Work_Fulfillment', 
                  'Recommendation_Score', 'Recognition', 'Growth_Potential']
    return df

df = load_data()

# Title
st.markdown('<div class="main-title">Homes First Employee Survey Dashboard</div>', unsafe_allow_html=True)

# Sidebar filters (UNCHANGED)
st.sidebar.header("Filters")
roles = ['All'] + sorted(df['Role'].unique().tolist())
role_filter = st.sidebar.selectbox("Role", roles)
ethnicities = ['All'] + sorted(df['Ethnicity'].unique().tolist())
ethnicity_filter = st.sidebar.selectbox("Ethnicity", ethnicities)
disabilities = ['All'] + sorted(df['Disability'].unique().tolist())
disability_filter = st.sidebar.selectbox("Disability", disabilities)

# Apply filters
filtered_df = df.copy()
if role_filter != 'All': filtered_df = filtered_df[filtered_df['Role'] == role_filter]
if ethnicity_filter != 'All': filtered_df = filtered_df[filtered_df['Ethnicity'] == ethnicity_filter]
if disability_filter != 'All': filtered_df = filtered_df[filtered_df['Disability'] == disability_filter]

# === NEW: KEY INSIGHTS SECTION ===
st.markdown("---")
st.header("🔍 Key Insights (Cross-Analysis)")

# Compute overall averages for comparisons
overall_rec = filtered_df['Recommendation_Score'].mean()
overall_recog = filtered_df['Recognition'].str.contains('Yes|yes', case=False, na=False).mean() * 100 if len(filtered_df) > 0 else 0

col1, col2 = st.columns(2)
with col1:
    st.info(f"**Overall Benchmarks** | Rec Score: {overall_rec:.1f} | Recognition: {overall_recog:.0f}%")

# AUTO-GENERATED INSIGHTS
insights = []

# 1. Ethnicity insights (top differences)
eth_groups = filtered_df.groupby('Ethnicity')['Recommendation_Score'].agg(['mean', 'count'])
eth_groups['delta'] = eth_groups['mean'] - overall_rec
sig_eth = eth_groups[abs(eth_groups['delta']) > 1].sort_values('delta', key=abs, ascending=False)
for eth, row in sig_eth.head(3).iterrows():
    delta_sign = "✅" if row['delta'] > 0 else "⚠️"
    insights.append(f"{delta_sign} {eth}: {row['mean']:.1f} ({row['delta']:+.1f} vs avg)")

# 2. Disability insights
dis_rec = filtered_df.groupby('Disability')['Recommendation_Score'].mean()
dis_rec['delta'] = dis_rec - overall_rec
sig_dis = dis_rec[abs(dis_rec['delta']) > 1].sort_values('delta')
for dis, delta in sig_dis.head(2).items():
    delta_sign = "⚠️" if delta < 0 else "✅"
    insights.append(f"{delta_sign} {dis}: {dis_rec[dis]:.1f} ({delta:+.1f} vs avg)")

# Display insights
for insight in insights[:6]:  # Top 6
    delta_type = "insight-positive" if "✅" in insight else "insight-negative"
    st.markdown(f'<div class="insight-card {delta_type}">{insight}</div>', unsafe_allow_html=True)

# === ORIGINAL METRIC CARDS (UNCHANGED) ===
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{len(filtered_df)}</div>
        <div class="metric-label">Total Responses</div>
    </div>
    """, unsafe_allow_html=True)
# ... [REST OF ORIGINAL METRIC CARDS UNCHANGED - keeping your exact code]

# [ALL YOUR ORIGINAL SECTIONS A-D REMAIN EXACTLY THE SAME]
# ... [helper functions, score bands, stacked bars, etc. - NO CHANGES]

# === NEW: CROSS-ANALYSIS CHARTS (AFTER ORIGINAL CONTENT) ===
st.markdown("---")
st.header("📊 Cross-Analysis: Demographics vs Scores")

tab1, tab2, tab3 = st.tabs(["Ethnicity", "Disability", "Correlations"])

with tab1:
    # Ethnicity vs Recommendation (BAR CHART)
    eth_avg = filtered_df.groupby('Ethnicity')['Recommendation_Score'].mean().sort_values(ascending=False).head(10)
    fig_eth = px.bar(x=eth_avg.index.str[:30], y=eth_avg.values, 
                     title="Avg Recommendation Score by Ethnicity",
                     labels={'x':'Ethnicity (truncated)', 'y':'Avg Score'})
    fig_eth.add_hline(y=overall_rec, line_dash="dash", line_color="red", 
                     annotation_text=f"Overall Avg: {overall_rec:.1f}")
    st.plotly_chart(fig_eth, use_container_width=True)

with tab2:
    # Disability distribution comparison
    fig_dis = px.histogram(filtered_df, x='Recommendation_Score', color='Disability',
                          title="Recommendation Score: With vs Without Disability",
                          facet_col='Disability', facet_col_wrap=2,
                          nbins=11, histnorm='percent')
    st.plotly_chart(fig_dis, use_container_width=True)

with tab3:
    # CORRELATION SCATTER: Recognition vs Recommendation
    recog_num = filtered_df['Recognition'].str.contains('Yes|yes', case=False).astype(int)
    fig_corr = px.scatter(filtered_df, x=recog_num, y='Recommendation_Score',
                         color='Role', title="Recognition vs Recommendation Score",
                         labels={'x':'Recognition (0=No, 1=Yes)', 'y':'Recommendation Score'})
    corr_val = filtered_df['Recommendation_Score'].corr(recog_num)
    st.plotly_chart(fig_corr, use_container_width=True)
    st.metric("Correlation Coefficient", f"{corr_val:.3f}")

# === NEW: LOW/HIGH SCORE DRIVERS TABLE ===
st.markdown("---")
st.subheader("Low & High Score Drivers by Group")
group_low_high = filtered_df.groupby(['Role', 'Disability']).agg({
    'Recommendation_Score': ['mean', lambda x: (x <= 4).mean()*100, lambda x: (x >= 9).mean()*100]
}).round(1)
group_low_high.columns = ['Avg', 'Low % (≤4)', 'High % (≥9)']
group_low_high['Flag'] = np.where(group_low_high['Avg'] < overall_rec-1.5, '⚠️', 
                                 np.where(group_low_high['Avg'] > overall_rec+1.5, '✅', ''))
st.dataframe(group_low_high.head(15), use_container_width=True)

# [YOUR ORIGINAL CONTEXT CHARTS AND FOOTER REMAIN EXACTLY THE SAME]
