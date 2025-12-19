import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# Page configuration & CSS
# =========================
st.set_page_config(page_title="Survey Cross-Analysis", page_icon="📊", layout="wide")

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

# =========================
# Data loading
# =========================
@st.cache_data
def load_data():
    df = pd.read_excel("Combined- Cross Analysis.xlsx")
    # Map original long question texts to simple column labels
    df.columns = [
        "Role",
        "Ethnicity",
        "Disability",
        "Work_Fulfillment",
        "Recommendation_Score",
        "Recognition",
        "Growth_Potential"
    ]
    return df

try:
    df = load_data()

    # =========================
    # Header
    # =========================
    st.title("📊 Employee Survey Cross-Analysis Dashboard")
    st.markdown("### Comparing employee groups across survey questions (using only the original answers).")

    # =========================
    # Sidebar filters
    # =========================
    st.sidebar.header("🔍 Filter Data")

    roles = ["All"] + sorted(df["Role"].dropna().unique().tolist())
    selected_role = st.sidebar.selectbox("Role/Department", roles)

    ethnicities = ["All"] + sorted(df["Ethnicity"].dropna().unique().tolist())
    selected_ethnicity = st.sidebar.selectbox("Ethnicity", ethnicities)

    disabilities = ["All"] + sorted(df["Disability"].dropna().unique().tolist())
    selected_disability = st.sidebar.selectbox("Disability", disabilities)

    # Apply filters
    filtered_df = df.copy()
    if selected_role != "All":
        filtered_df = filtered_df[filtered_df["Role"] == selected_role]
    if selected_ethnicity != "All":
        filtered_df = filtered_df[filtered_df["Ethnicity"] == selected_ethnicity]
    if selected_disability != "All":
        filtered_df = filtered_df[filtered_df["Disability"] == selected_disability]

    total = len(filtered_df)

    # =========================
    # Key metrics
    # =========================
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Responses</div>
                <div class="metric-value">{total}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        avg_score = filtered_df["Recommendation_Score"].mean() if total > 0 else 0
        st.markdown(f"""
            <div class="metric-card metric-card-blue">
                <div class="metric-label">Avg Recommendation (0–10)</div>
                <div class="metric-value">{avg_score:.1f}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        # Simple count of lowest vs highest answers (still only dataset values)
        low_rec = len(filtered_df[filtered_df["Recommendation_Score"] <= 6]) if total > 0 else 0
        high_rec = len(filtered_df[filtered_df["Recommendation_Score"] >= 9]) if total > 0 else 0
        st.markdown(f"""
            <div class="metric-card metric-card-orange">
                <div class="metric-label">Low vs High Recommenders</div>
                <div class="metric-value">{low_rec}:{high_rec}</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        fulfilled = len(
            filtered_df[
                filtered_df["Work_Fulfillment"]
                .astype(str)
                .str.contains("extremely", case=False, na=False)
            ]
        ) if total > 0 else 0
        pct = (fulfilled / total * 100) if total > 0 else 0
        st.markdown(f"""
            <div class="metric-card metric-card-green">
                <div class="metric-label">“Extremely fulfilling”</div>
                <div class="metric-value">{pct:.0f}%</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # =========================
    # Helper: 100% stacked bar
    # =========================
    def stacked_percent_bar(df_in, group_col, question_col, title):
        sub = df_in[[group_col, question_col]].dropna().copy()
        if sub.empty:
            st.info(f"No data available for {title} with current filters.")
            return

        tab = pd.crosstab(sub[group_col], sub[question_col], normalize="index") * 100
        long_df = tab.reset_index().melt(
            id_vars=group_col, var_name="Answer", value_name="Percent"
        )

        fig = px.bar(
            long_df,
            x="Percent",
            y=group_col,
            color="Answer",
            orientation="h",
            barmode="stack",
            labels={"Percent": "Percentage of respondents"},
            title=title,
        )
        fig.update_layout(
            xaxis_tickformat=".0f",
            yaxis=dict(automargin=True),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # 1. Recommendation Score
    # =========================
    st.header("How likely are you to recommend Homes First as a good place to work?")

    if total > 0 and filtered_df["Recommendation_Score"].notna().any():
        rec_counts = (
            filtered_df["Recommendation_Score"]
            .dropna()
            .astype(int)
            .value_counts()
            .sort_index()
            .reset_index()
        )
        rec_counts.columns = ["Score", "Count"]

        fig_rec = px.bar(
            rec_counts,
            x="Score",
            y="Count",
            labels={"Count": "Number of respondents"},
            title="Distribution of recommendation scores (0–10)",
        )
        fig_rec.update_layout(yaxis=dict(automargin=True))
        st.plotly_chart(fig_rec, use_container_width=True)

        # Recommendation by Role – still just counts/percentages of the original scores
        st.subheader("Recommendation scores by role")
        stacked_percent_bar(
            filtered_df, "Role", "Recommendation_Score",
            "Recommendation score distribution by role (%)"
        )
    else:
        st.info("No recommendation data for the current filters.")

    st.markdown("---")

    # =========================
    # 2. Work Fulfillment
    # =========================
    st.header("How fulfilling and rewarding do you find your work?")

    stacked_percent_bar(
        filtered_df,
        "Role",
        "Work_Fulfillment",
        "Work fulfillment distribution by role (%)"
    )

    st.markdown("---")

    # =========================
    # 3. Recognition
    # =========================
    st.header("Do you feel you get acknowledged and recognized for your contribution at work?")

    stacked_percent_bar(
        filtered_df,
        "Role",
        "Recognition",
        "Recognition distribution by role (%)"
    )

    st.markdown("---")

    # =========================
    # 4. Growth Potential
    # =========================
    st.header("Do you feel there is potential for growth at Homes First?")

    stacked_percent_bar(
        filtered_df,
        "Role",
        "Growth_Potential",
        "Growth potential distribution by role (%)"
    )

    st.markdown("---")

    # =========================
    # 5. Optional: Ethnicity and Disability overview
    # =========================
    st.header("Context: who answered the survey?")

    col_ctx1, col_ctx2 = st.columns(2)

    with col_ctx1:
        eth_counts = (
            filtered_df["Ethnicity"]
            .dropna()
            .value_counts()
            .reset_index()
            .rename(columns={"index": "Ethnicity", "Ethnicity": "Count"})
        )
        if not eth_counts.empty:
            fig_eth = px.bar(
                eth_counts,
                y="Ethnicity",
                x="Count",
                orientation="h",
                title="Number of respondents by ethnicity",
            )
            fig_eth.update_layout(yaxis=dict(automargin=True))
            st.plotly_chart(fig_eth, use_container_width=True)
        else:
            st.info("No ethnicity data for the current filters.")

    with col_ctx2:
        dis_counts = (
            filtered_df["Disability"]
            .dropna()
            .value_counts()
            .reset_index()
            .rename(columns={"index": "Disability", "Disability": "Count"})
        )
        if not dis_counts.empty:
            fig_dis = px.bar(
                dis_counts,
                y="Disability",
                x="Count",
                orientation="h",
                title="Number of respondents by disability status/type",
            )
            fig_dis.update_layout(yaxis=dict(automargin=True))
            st.plotly_chart(fig_dis, use_container_width=True)
        else:
            st.info("No disability data for the current filters.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Cross-Analysis Dashboard – Simple view**")

except FileNotFoundError:
    st.error("❌ File not found: 'Combined- Cross Analysis.xlsx'")
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
