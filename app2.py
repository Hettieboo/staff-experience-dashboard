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
    h2 {color: #34495e; padding-top: 25px; padding-bottom: 15px;}
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel("Combined- Cross Analysis.xlsx")
    df.columns = [
        'Role', 'Ethnicity', 'Disability',
        'Work_Fulfillment', 'Recommendation_Score',
        'Recognition', 'Growth_Potential'
    ]
    return df

try:
    df = load_data()

    # Header
    st.title("📊 Employee Survey Cross-Analysis Dashboard")
    st.markdown("### Comparing Employee Groups Across Survey Questions")

    # Sidebar filters
    st.sidebar.header("🔍 Filter Data")
    roles = ['All'] + sorted(df['Role'].dropna().unique())
    selected_role = st.sidebar.selectbox("Role/Department", roles)

    ethnicities = ['All'] + sorted(df['Ethnicity'].dropna().unique())
    selected_ethnicity = st.sidebar.selectbox("Ethnicity", ethnicities)

    # Apply filters
    filtered_df = df.copy()
    if selected_role != 'All':
        filtered_df = filtered_df[filtered_df['Role'] == selected_role]
    if selected_ethnicity != 'All':
        filtered_df = filtered_df[filtered_df['Ethnicity'] == selected_ethnicity]

    total = len(filtered_df)

    # ===============================
    # METRICS
    # ===============================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Responses", total)
    col2.metric("Avg Recommendation", f"{filtered_df['Recommendation_Score'].mean():.1f}/10")

    promoters = len(filtered_df[filtered_df['Recommendation_Score'] >= 9])
    detractors = len(filtered_df[filtered_df['Recommendation_Score'] <= 6])
    nps = ((promoters - detractors) / total * 100) if total else 0
    col3.metric("NPS Score", f"{nps:.0f}")

    fulfilled_pct = (
        filtered_df['Work_Fulfillment']
        .str.contains('extremely', case=False, na=False)
        .mean() * 100 if total else 0
    )
    col4.metric("Highly Fulfilled", f"{fulfilled_pct:.0f}%")

    st.divider()

    # ===============================
    # SECTION 1: RECOMMENDATION SCORES
    # ===============================
    st.markdown("## 🎯 Recommendation Score Across Groups")

    col1, col2 = st.columns(2)

    with col1:
        role_avg = (
            df.groupby('Role')['Recommendation_Score']
            .agg(['mean', 'count'])
            .query("count >= 3")
            .sort_values('mean')
            .tail(10)
            .reset_index()
        )

        fig1 = px.bar(
            role_avg,
            y='Role',
            x='mean',
            orientation='h',
            text=role_avg['mean'].round(1),
            color='mean',
            color_continuous_scale='RdYlGn',
            range_color=[0, 10],
            height=520
        )

        fig1.update_layout(
            title="Average Recommendation Score by Role",
            xaxis_title="Score (0–10)",
            yaxis_title="",
            margin=dict(l=260, r=40, t=80, b=40),
            showlegend=False
        )

        fig1.update_traces(textposition="outside")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        eth_avg = (
            df.groupby('Ethnicity')['Recommendation_Score']
            .agg(['mean', 'count'])
            .query("count >= 3")
            .sort_values('mean')
            .tail(10)
            .reset_index()
        )

        fig2 = px.bar(
            eth_avg,
            y='Ethnicity',
            x='mean',
            orientation='h',
            text=eth_avg['mean'].round(1),
            color='mean',
            color_continuous_scale='RdYlGn',
            range_color=[0, 10],
            height=520
        )

        fig2.update_layout(
            title="Average Recommendation Score by Ethnicity",
            xaxis_title="Score (0–10)",
            yaxis_title="",
            margin=dict(l=260, r=40, t=80, b=40),
            showlegend=False
        )

        fig2.update_traces(textposition="outside")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ===============================
    # SECTION 3: RECOGNITION & GROWTH
    # ===============================
    st.markdown("## 🌟 Recognition & Growth Sentiment Across Groups")
    st.markdown("<div style='margin-bottom:30px;'></div>", unsafe_allow_html=True)

    top_roles = df['Role'].value_counts().head(8).index

    recog_map = {
        "Yes, I do feel recognized and acknowledged": "Yes",
        "I somewhat feel recognized and acknowledged": "Somewhat",
        "I do find myself being recognized and acknowledged, but it's rare given the contributions I make": "Rare",
        "I don't feel recognized and acknowledged and would prefer staff successes to be highlighted more frequently": "No – Want More",
        "I don't feel recognized and acknowledged but I prefer it that way": "No – Prefer"
    }

    growth_map = {
        "Yes, I do feel there is potential to grow and I hope to advance my career with Homes First": "Yes",
        "There is some potential to grow and I hope to advance my career with Homes First": "Some",
        "Potential to grow seems limited at Homes First and I will likely need to advance my career with another organization": "Limited",
        "There is very little potential to grow although I would like to advance my career with Homes First": "Very Limited",
        "I am not interested in career growth and prefer to remain in my current role": "Not Interested"
    }

    def contrast_color(val):
        return "white" if val >= 45 else "black"

    def heatmap(data, title):
        z = data.values
        text_colors = [[contrast_color(v) for v in row] for row in z]

        fig = go.Figure(go.Heatmap(
            z=z,
            x=data.columns,
            y=data.index,
            colorscale="RdYlGn",
            text=z.round(0),
            texttemplate="%{text}%",
            textfont=dict(color=text_colors, size=12),
            hovertemplate="%{y}<br>%{x}: %{z:.1f}%<extra></extra>"
        ))

        fig.update_layout(
            title=title,
            height=560,
            margin=dict(t=120, l=260, r=40, b=40),
            yaxis=dict(autorange="reversed")
        )
        return fig

    df['Recognition_Short'] = df['Recognition'].map(recog_map)
    df['Growth_Short'] = df['Growth_Potential'].map(growth_map)

    recog_cross = pd.crosstab(
        df[df['Role'].isin(top_roles)]['Role'],
        df[df['Role'].isin(top_roles)]['Recognition_Short'],
        normalize='index'
    ) * 100

    growth_cross = pd.crosstab(
        df[df['Role'].isin(top_roles)]['Role'],
        df[df['Role'].isin(top_roles)]['Growth_Short'],
        normalize='index'
    ) * 100

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(heatmap(recog_cross, "Recognition Sentiment by Role (%)"), True)

    with col2:
        st.plotly_chart(heatmap(growth_cross, "Growth Perception by Role (%)"), True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Cross-Analysis Dashboard v1.1**")

except FileNotFoundError:
    st.error("❌ File not found: Combined- Cross Analysis.xlsx")
except Exception as e:
    st.error(f"❌ Error: {e}")
