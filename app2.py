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
    # Sidebar filters
    # ----------------------
    st.sidebar.header("🔍 Filter Data")
    role_col = 'Select the role/department that best describes your current position at Homes First.'
    ethnicity_col = 'Which racial or ethnic identity/identities best reflect you. (Select all that apply.)'
    disability_col = 'Do you identify as an individual living with a disability/disabilities and if so, what type of disability/disabilities do you have? (Select all that apply.)'
    work_col = 'How fulfilling and rewarding do you find your work?'
    rec_col = 'How likely are you to recommend Homes First as a good place to work?'
    recog_col = 'Do you feel you get acknowledged and recognized for your contribution  at work?'
    growth_col = 'Do you feel there is potential for growth at Homes First?'

    roles = ['All'] + sorted(df[role_col].dropna().unique().tolist())
    selected_role = st.sidebar.selectbox("Role/Department", roles)

    ethnicities = ['All'] + sorted(set([e.strip() for sublist in df[ethnicity_col].dropna().str.split(',') for e in sublist]))
    selected_ethnicity = st.sidebar.selectbox("Ethnicity", ethnicities)

    disabilities = ['All'] + sorted(set([d.strip() for sublist in df[disability_col].dropna().str.split(',') for d in sublist]))
    selected_disability = st.sidebar.selectbox("Disability", disabilities)

    # Filter the dataframe
    filtered_df = df.copy()
    if selected_role != 'All':
        filtered_df = filtered_df[filtered_df[role_col] == selected_role]
    if selected_ethnicity != 'All':
        filtered_df = filtered_df[filtered_df[ethnicity_col].str.contains(selected_ethnicity, na=False)]
    if selected_disability != 'All':
        filtered_df = filtered_df[filtered_df[disability_col].str.contains(selected_disability, na=False)]

    # ----------------------
    # Header and metrics
    # ----------------------
    st.title("📊 Employee Survey Cross-Analysis Dashboard")
    st.markdown("### Compare Employee Groups Across Survey Questions")

    total = len(filtered_df)

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
    # Dynamic cross-analysis
    # ----------------------
    st.sidebar.markdown("### 🎛 Select Questions for Analysis")
    survey_questions = [work_col, rec_col, recog_col, growth_col]
    x_question = st.sidebar.selectbox("X-axis Question", survey_questions, index=0)
    y_question = st.sidebar.selectbox("Y-axis Question", survey_questions, index=1 if len(survey_questions)>1 else 0)

    chart_type = st.sidebar.radio("Chart Type", ['Bar', 'Stacked Bar', 'Heatmap', 'Scatter'])

    st.markdown(f"## 📈 {x_question} vs {y_question}")

    # Create chart
    if chart_type == 'Bar':
        if filtered_df[y_question].dtype in [int, float]:
            agg_df = filtered_df.groupby(role_col)[y_question].mean().reset_index()
            fig = px.bar(agg_df, x=y_question, y=role_col, orientation='h', text=y_question, title=f"Average {y_question} by Role")
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
        else:
            agg_df = pd.crosstab(filtered_df[role_col], filtered_df[y_question])
            fig = px.bar(agg_df, y=agg_df.index, x=agg_df.columns, orientation='h', title=f"{y_question} Distribution by Role", text_auto=True)
    elif chart_type == 'Stacked Bar':
        agg_df = pd.crosstab(filtered_df[role_col], filtered_df[y_question], normalize='index')*100
        fig = go.Figure()
        colors = px.colors.qualitative.Pastel
        for i, col in enumerate(agg_df.columns):
            fig.add_trace(go.Bar(
                y=[r[:35] for r in agg_df.index],
                x=agg_df[col],
                name=col,
                orientation='h',
                marker_color=colors[i % len(colors)],
                text=[f'{v:.0f}%' for v in agg_df[col]],
                textposition='inside'
            ))
        fig.update_layout(barmode='stack', xaxis_title="Percentage", yaxis_title="", height=500, title=f"{y_question} by Role (%)")
    elif chart_type == 'Heatmap':
        agg_df = pd.crosstab(filtered_df[role_col], filtered_df[y_question], normalize='index')*100
        fig = go.Figure(go.Heatmap(
            z=agg_df.values,
            x=agg_df.columns,
            y=[r[:50] for r in agg_df.index],
            colorscale='RdYlGn',
            text=[[f'{v:.0f}%' for v in row] for row in agg_df.values],
            texttemplate='%{text}',
            textfont={"size":11},
            hovertemplate='<b>%{y}</b><br>%{x}: %{z:.1f}%<extra></extra>'
        ))
        fig.update_layout(title=f"{y_question} by Role (%)", xaxis_title=y_question, yaxis_title="", height=700)
    elif chart_type == 'Scatter':
        if filtered_df[y_question].dtype in [int,float] and filtered_df[x_question].dtype in [int,float]:
            fig = px.scatter(filtered_df, x=x_question, y=y_question, color=role_col, hover_data=[ethnicity_col, disability_col])
        else:
            st.warning("Scatter plot requires numeric fields for X and Y.")
            fig = go.Figure()

    st.plotly_chart(fig, use_container_width=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Dynamic Cross-Analysis Dashboard v2.0**")

except FileNotFoundError:
    st.error("❌ File not found: 'Combined- Cross Analysis.xlsx'")
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
