import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------------
# Page configuration
# ----------------------
st.set_page_config(page_title="Survey Cross-Analysis", page_icon="📊", layout="wide")

# Custom CSS
st.markdown("""
<style>
.main {padding: 0rem 1rem;}
h1 {color: #2c3e50; padding-bottom: 10px;}
h2 {color: #34495e; padding-top: 15px; padding-bottom: 10px;}
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 10px;
}
.metric-card-green {background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);}
.metric-card-blue {background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);}
.metric-card-orange {background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);}
.metric-value {font-size: 2.5em; font-weight: bold; margin: 10px 0;}
.metric-label {font-size: 0.9em; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px;}
</style>
""", unsafe_allow_html=True)

# ----------------------
# Load data
# ----------------------
@st.cache_data
def load_data():
    df = pd.read_excel('Combined- Cross Analysis.xlsx')
    return df

try:
    df = load_data()

    # ----------------------
    # Column names
    # ----------------------
    role_col = 'Select the role/department that best describes your current position at Homes First.'
    ethnicity_col = 'Which racial or ethnic identity/identities best reflect you. (Select all that apply.)'
    disability_col = 'Do you identify as an individual living with a disability/disabilities and if so, what type of disability/disabilities do you have? (Select all that apply.)'
    work_col = 'How fulfilling and rewarding do you find your work?'
    rec_col = 'How likely are you to recommend Homes First as a good place to work?'
    recog_col = 'Do you feel you get acknowledged and recognized for your contribution  at work?'
    growth_col = 'Do you feel there is potential for growth at Homes First?'

    # ----------------------
    # Define red-yellow-green gradient manually
    # ----------------------
    rdylgn_colors = ['#d73027', '#fc8d59', '#fee08b', '#91cf60', '#1a9850']

    # ----------------------
    # Sidebar filters
    # ----------------------
    st.sidebar.header("🔍 Filter Data")
    roles = ['All'] + sorted(df[role_col].dropna().unique().tolist())
    selected_role = st.sidebar.selectbox("Role/Department", roles)

    ethnicities = ['All'] + sorted(set([e.strip() for sublist in df[ethnicity_col].dropna().str.split(',') for e in sublist]))
    selected_ethnicity = st.sidebar.selectbox("Ethnicity", ethnicities)

    disabilities = ['All'] + sorted(set([d.strip() for sublist in df[disability_col].dropna().str.split(',') for d in sublist]))
    selected_disability = st.sidebar.selectbox("Disability", disabilities)

    # ----------------------
    # Filter DataFrame
    # ----------------------
    filtered_df = df.copy()
    if selected_role != 'All':
        filtered_df = filtered_df[filtered_df[role_col] == selected_role]
    if selected_ethnicity != 'All':
        filtered_df = filtered_df[filtered_df[ethnicity_col].str.contains(selected_ethnicity, na=False)]
    if selected_disability != 'All':
        filtered_df = filtered_df[filtered_df[disability_col].str.contains(selected_disability, na=False)]

    total = len(filtered_df)

    # ----------------------
    # Metrics
    # ----------------------
    st.title("📊 Employee Survey Cross-Analysis Dashboard")
    st.markdown("### Compare Employee Groups Across Survey Questions")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Total Responses</div><div class='metric-value'>{total}</div></div>", unsafe_allow_html=True)
    with col2:
        avg_score = filtered_df[rec_col].mean() if total > 0 else 0
        st.markdown(f"<div class='metric-card metric-card-blue'><div class='metric-label'>Avg Recommendation</div><div class='metric-value'>{avg_score:.1f}/10</div></div>", unsafe_allow_html=True)
    with col3:
        promoters = len(filtered_df[filtered_df[rec_col] >= 9])
        detractors = len(filtered_df[filtered_df[rec_col] <= 6])
        nps = ((promoters - detractors) / total * 100) if total > 0 else 0
        nps_color = "metric-card-green" if nps > 20 else "metric-card-orange" if nps > 0 else "metric-card"
        st.markdown(f"<div class='metric-card {nps_color}'><div class='metric-label'>NPS Score</div><div class='metric-value'>{nps:.0f}</div></div>", unsafe_allow_html=True)
    with col4:
        fulfilled = len(filtered_df[filtered_df[work_col].str.contains('extremely', case=False, na=False)])
        pct = (fulfilled/total*100) if total > 0 else 0
        st.markdown(f"<div class='metric-card metric-card-green'><div class='metric-label'>Highly Fulfilled</div><div class='metric-value'>{pct:.0f}%</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    # ----------------------
    # Horizontal Bar: Recommendation by Role
    # ----------------------
    role_avg = filtered_df.groupby(role_col)[rec_col].mean().reset_index()
    height = max(400, 60*len(role_avg)+150)
    fig_bar = px.bar(role_avg,
                     x=rec_col,
                     y=role_col,
                     orientation='h',
                     text=rec_col,
                     color=rec_col,
                     color_continuous_scale=rdylgn_colors,
                     range_color=[0,10],
                     title="Average Recommendation by Role")
    fig_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_bar.update_layout(height=height, margin=dict(l=250, r=50, t=100, b=50), yaxis=dict(automargin=True))
    st.plotly_chart(fig_bar, use_container_width=True)

    # ----------------------
    # Donut: Recognition
    # ----------------------
    fig_donut = px.pie(
        filtered_df,
        names=recog_col,
        title="Recognition Distribution",
        hole=0.5,
        color_discrete_sequence=rdylgn_colors
    )
    fig_donut.update_traces(
        textposition='outside',
        textinfo='percent+label',
        pull=[0.05]*len(filtered_df[recog_col].unique())
    )
    fig_donut.update_layout(
        height=600,
        width=600,
        margin=dict(t=100, b=50, l=50, r=50),
        title={'x':0.5, 'xanchor':'center'}
    )
    st.plotly_chart(fig_donut, use_container_width=False)

    # ----------------------
    # Stacked Horizontal Bar: Growth Potential
    # ----------------------
    growth_cross = pd.crosstab(filtered_df[role_col], filtered_df[growth_col], normalize='index')*100
    fig_stack = go.Figure()
    for i, col in enumerate(growth_cross.columns):
        fig_stack.add_trace(go.Bar(
            y=[r[:50] for r in growth_cross.index],
            x=growth_cross[col],
            name=col,
            orientation='h',
            marker_color=rdylgn_colors[i % len(rdylgn_colors)],
            text=[f'{v:.0f}%' if v>=5 else '' for v in growth_cross[col]],
            textposition='inside'
        ))
    height = max(400, 60*len(growth_cross)+150)
    fig_stack.update_layout(barmode='stack',
                            xaxis_title="Percentage",
                            yaxis_title="",
                            height=height,
                            margin=dict(l=250, r=50, t=100, b=50),
                            title="Growth Potential by Role (%)")
    st.plotly_chart(fig_stack, use_container_width=True)

    # ----------------------
    # Stacked Horizontal Bar: Work Fulfillment
    # ----------------------
    fulfill_cross = pd.crosstab(filtered_df[role_col], filtered_df[work_col], normalize='index')*100
    fig_fulfill = go.Figure()
    for i, col in enumerate(fulfill_cross.columns):
        fig_fulfill.add_trace(go.Bar(
            y=[r[:50] for r in fulfill_cross.index],
            x=fulfill_cross[col],
            name=col,
            orientation='h',
            marker_color=rdylgn_colors[i % len(rdylgn_colors)],
            text=[f'{v:.0f}%' if v>=5 else '' for v in fulfill_cross[col]],
            textposition='inside'
        ))
    height = max(400, 60*len(fulfill_cross)+150)
    fig_fulfill.update_layout(barmode='stack',
                              xaxis_title="Percentage",
                              yaxis_title="",
                              height=height,
                              margin=dict(l=250, r=50, t=100, b=50),
                              title="Work Fulfillment by Role (%)")
    st.plotly_chart(fig_fulfill, use_container_width=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Cross-Analysis Dashboard v10.0**")

except FileNotFoundError:
    st.error("❌ File not found: 'Combined- Cross Analysis.xlsx'")
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
