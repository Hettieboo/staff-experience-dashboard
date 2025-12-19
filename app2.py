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
    df.columns = [
        "Role",
        "Ethnicity",
        "Disability",
        "Work_Fulfillment",
        "Recommendation_Score",
        "Recognition",
        "Growth_Potential",
    ]
    return df

df = load_data()

# =========================
# Header
# =========================
st.title("📊 Employee Survey Cross-Analysis Dashboard")
st.markdown("### Clear charts by department for each survey question.[file:21]")

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
    if total > 0:
        low = len(filtered_df[filtered_df["Recommendation_Score"] <= 4])
        high = len(filtered_df[filtered_df["Recommendation_Score"] >= 8])
    else:
        low = high = 0
    st.markdown(f"""
        <div class="metric-card metric-card-orange">
            <div class="metric-label">Low vs High Scores (≤4 / ≥8)</div>
            <div class="metric-value">{low}:{high}</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    if total > 0:
        fulfilled = len(
            filtered_df[
                filtered_df["Work_Fulfillment"]
                .astype(str)
                .str.contains("extremely", case=False, na=False)
            ]
        )
        pct_full = fulfilled / total * 100
    else:
        pct_full = 0
    st.markdown(f"""
        <div class="metric-card metric-card-green">
            <div class="metric-label">“Extremely fulfilling”</div>
            <div class="metric-value">{pct_full:.0f}%</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# =========================
# Helper: 100% stacked horizontal bar with large bars
# =========================
def stacked_percent_bar(df_in, group_col, question_col, title, top_n=10):
    sub = df_in[[group_col, question_col]].dropna().copy()
    if sub.empty:
        st.info(f"No data for {title} with current filters.")
        return

    # focus on the roles with most data so bars can be large
    top_groups = sub[group_col].value_counts().head(top_n).index
    sub = sub[sub[group_col].isin(top_groups)]

    tab = pd.crosstab(sub[group_col], sub[question_col], normalize="index") * 100
    long_df = tab.reset_index().melt(
        id_vars=group_col, var_name="Answer", value_name="Percent"
    )

    height = max(400, 45 * tab.shape[0] + 120)

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
        height=height,
        xaxis_tickformat=".0f",
        yaxis=dict(automargin=True),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=10),
        ),
        margin=dict(l=260, r=40, t=70, b=90),
    )
    st.plotly_chart(fig, use_container_width=True)

# =========================
# 1. Recommendation – keep first chart, then add grouped
# =========================
st.header("How likely are you to recommend Homes First as a good place to work?")

if total > 0 and filtered_df["Recommendation_Score"].notna().any():
    # First chart (already good): simple distribution 0–10
    rec_counts = (
        filtered_df["Recommendation_Score"]
        .dropna()
        .astype(int)
        .value_counts()
        .sort_index()
        .reset_index()
    )
    rec_counts.columns = ["Score", "Count"]

    col_rec1, col_rec2 = st.columns(2)

    with col_rec1:
        fig_rec = px.bar(
            rec_counts,
            x="Score",
            y="Count",
            labels={"Count": "Number of respondents"},
            title="Score distribution (0–10)",
        )
        fig_rec.update_layout(yaxis=dict(automargin=True))
        st.plotly_chart(fig_rec, use_container_width=True)

    with col_rec2:
        # Donut by score bands (still using raw scores, just grouped)
        rec_band = rec_counts.copy()
        rec_band["Band"] = pd.cut(
            rec_band["Score"],
            bins=[-1, 3, 6, 8, 10],
            labels=["0–3", "4–6", "7–8", "9–10"],
        )
        band_counts = rec_band.groupby("Band")["Count"].sum().reset_index()
        band_counts = band_counts[band_counts["Band"].notna()]

        if not band_counts.empty:
            fig_donut = px.pie(
                band_counts,
                names="Band",
                values="Count",
                hole=0.5,
                title="Score bands (0–3, 4–6, 7–8, 9–10)",
            )
            fig_donut.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("Not enough data to show the donut chart.")

    st.subheader("Score bands by department (big horizontal bars)")
    # banded stacked bar by Role – this is where roles are clearly visible
    sub = filtered_df[["Role", "Recommendation_Score"]].dropna().copy()
    sub["Score_band"] = pd.cut(
        sub["Recommendation_Score"].astype(int),
        bins=[-1, 3, 6, 8, 10],
        labels=["0–3", "4–6", "7–8", "9–10"],
    )
    stacked_percent_bar(
        sub.rename(columns={"Score_band": "Score band"}),
        "Role",
        "Score band",
        "Recommendation score bands by role (%)",
        top_n=10,
    )
else:
    st.info("No recommendation data for the current filters.")

st.markdown("---")

# =========================
# 2. Work Fulfillment – big stacked bars by role
# =========================
st.header("How fulfilling and rewarding do you find your work?")

stacked_percent_bar(
    filtered_df,
    "Role",
    "Work_Fulfillment",
    "Work fulfillment distribution by role (%)",
    top_n=10,
)

st.markdown("---")

# =========================
# 3. Recognition – big stacked bars by role
# =========================
st.header("Do you feel you get acknowledged and recognized for your contribution at work?")

stacked_percent_bar(
    filtered_df,
    "Role",
    "Recognition",
    "Recognition distribution by role (%)",
    top_n=10,
)

st.markdown("---")

# =========================
# 4. Growth Potential – big stacked bars by role
# =========================
st.header("Do you feel there is potential for growth at Homes First?")

stacked_percent_bar(
    filtered_df,
    "Role",
    "Growth_Potential",
    "Growth potential distribution by role (%)",
    top_n=10,
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Cross-Analysis Dashboard – Departments clearly visible**")
