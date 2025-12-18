import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import textwrap

# ----------------------
# Global Plotly style
# ----------------------
pio.templates.default = "plotly_white"
PLOTLY_TEMPLATE = "plotly_white"

PRIMARY_SEQ = ["#4facfe"]
SECONDARY_SEQ = ["#00b4d8"]

# ----------------------
# Helpers
# ----------------------
def wrap_label(label, width=30):
    if not isinstance(label, str):
        return label
    return "<br>".join(textwrap.wrap(label, width=width))

def split_multi(series):
    return sorted(set(
        e.strip()
        for sublist in series.dropna().astype(str).str.split(',')
        for e in sublist if e.strip()
    ))


# ----------------------
# Page configuration
# ----------------------
st.set_page_config(
    page_title="Survey Cross-Analysis",
    page_icon="📊",
    layout="wide"
)

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
    df = pd.read_excel("Combined- Cross Analysis.xlsx")
    return df

try:
    df = load_data()

    # ----------------------
    # Column names
    # ----------------------
    role_col = "Select the role/department that best describes your current position at Homes First."
    ethnicity_col = "Which racial or ethnic identity/identities best reflect you. (Select all that apply.)"
    disability_col = "Do you identify as an individual living with a disability/disabilities and if so, what type of disability/disabilities do you have? (Select all that apply.)"
    work_col = "How fulfilling and rewarding do you find your work?"
    rec_col = "How likely are you to recommend Homes First as a good place to work?"
    recog_col = "Do you feel you get acknowledged and recognized for your contribution  at work?"
    growth_col = "Do you feel there is potential for growth at Homes First?"

    # ----------------------
    # Sidebar filters
    # ----------------------
    st.sidebar.header("🔍 Filter Data")

    roles = ["All"] + sorted(df[role_col].dropna().unique().tolist())
    selected_role = st.sidebar.selectbox("Role/Department", roles)

    ethnicities = ["All"] + split_multi(df[ethnicity_col])
    selected_ethnicity = st.sidebar.selectbox("Ethnicity", ethnicities)

    disabilities = ["All"] + split_multi(df[disability_col])
    selected_disability = st.sidebar.selectbox("Disability", disabilities)

    filtered_df = df.copy()
    if selected_role != "All":
        filtered_df = filtered_df[filtered_df[role_col] == selected_role]
    if selected_ethnicity != "All":
        filtered_df = filtered_df[
            filtered_df[ethnicity_col].astype(str).str.contains(selected_ethnicity, na=False)
        ]
    if selected_disability != "All":
        filtered_df = filtered_df[
            filtered_df[disability_col].astype(str).str.contains(selected_disability, na=False)
        ]

    total = len(filtered_df)

    # ----------------------
    # Title & key metrics
    # ----------------------
    st.title("📊 Employee Survey Cross-Analysis Dashboard")
    st.markdown(
        "Explore how different employee groups respond across key survey questions such as recommendation, recognition, and growth.[file:21]"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"<div class='metric-card'><div class='metric-label'>Total Responses</div>"
            f"<div class='metric-value'>{total}</div></div>",
            unsafe_allow_html=True,
        )

    with col2:
        avg_score = filtered_df[rec_col].mean() if total > 0 else 0
        st.markdown(
            f"<div class='metric-card metric-card-blue'><div class='metric-label'>Avg Recommendation</div>"
            f"<div class='metric-value'>{avg_score:.1f}/10</div></div>",
            unsafe_allow_html=True,
        )

    with col3:
        promoters = len(filtered_df[filtered_df[rec_col] >= 9]) if total > 0 else 0
        detractors = len(filtered_df[filtered_df[rec_col] <= 6]) if total > 0 else 0
        nps = ((promoters - detractors) / total * 100) if total > 0 else 0
        nps_color = (
            "metric-card-green" if nps > 20
            else "metric-card-orange" if nps > 0
            else "metric-card"
        )
        st.markdown(
            f"<div class='metric-card {nps_color}'><div class='metric-label'>NPS Score</div>"
            f"<div class='metric-value'>{nps:.0f}</div></div>",
            unsafe_allow_html=True,
        )

    with col4:
        fulfilled = (
            len(
                filtered_df[
                    filtered_df[work_col]
                    .astype(str)
                    .str.contains("extremely", case=False, na=False)
                ]
            )
            if total > 0
            else 0
        )
        pct = (fulfilled / total * 100) if total > 0 else 0
        st.markdown(
            f"<div class='metric-card metric-card-green'><div class='metric-label'>Highly Fulfilled</div>"
            f"<div class='metric-value'>{pct:.0f}%</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ----------------------
    # Recommendation behaviour
    # ----------------------
    st.header("Recommendation behaviour")
    st.caption(
        "See how recommendation scores are distributed and how they differ by role and demographic groups.[file:21]"
    )

    # 1) Distribution 0–10 (this is your existing first chart, kept)
    if total > 0 and filtered_df[rec_col].notna().any():
        rec_dist = (
            filtered_df[rec_col]
            .dropna()
            .astype(int)
            .value_counts()
            .sort_index()
            .reset_index()
        )
        rec_dist.columns = ["Score", "Count"]
        rec_dist["Group"] = pd.cut(
            rec_dist["Score"],
            bins=[-1, 6, 8, 10],
            labels=["Detractor (0–6)", "Passive (7–8)", "Promoter (9–10)"],
        )

        st.subheader("Recommendation score distribution")
        st.caption(
            "Breakdown of scores from 0–10 into detractors, passives, and promoters for the selected filters.[file:21]"
        )

        fig_rec_dist = px.bar(
            rec_dist,
            x="Score",
            y="Count",
            color="Group",
            color_discrete_map={
                "Detractor (0–6)": "#d73027",
                "Passive (7–8)": "#fee08b",
                "Promoter (9–10)": "#1a9850",
            },
            labels={"Count": "Number of responses"},
            template=PLOTLY_TEMPLATE,
        )
        fig_rec_dist.update_layout(margin=dict(l=20, r=20, t=40, b=40))
        st.plotly_chart(fig_rec_dist, use_container_width=True)
    else:
        st.info("No recommendation data for the current filters.")

    # 2) Recommendation by role – box + NPS 100% stacked
    if total > 0 and filtered_df[role_col].notna().any() and filtered_df[rec_col].notna().any():
        tmp = filtered_df[[role_col, rec_col]].dropna().copy()
        tmp["nps_group"] = pd.cut(
            tmp[rec_col].astype(int),
            bins=[-1, 6, 8, 10],
            labels=["Detractor (0–6)", "Passive (7–8)", "Promoter (9–10)"],
        )

        st.subheader("Recommendation scores by role (0–10)")
        st.caption(
            "Box plot shows the spread of recommendation scores within each role, including medians and outliers.[file:21]"
        )

        fig_box = px.box(
            tmp,
            x=role_col,
            y=rec_col,
            points="all",
            color_discrete_sequence=PRIMARY_SEQ,
            template=PLOTLY_TEMPLATE,
        )
        fig_box.update_layout(
            xaxis_title="Role",
            yaxis_title="Score (0–10)",
            xaxis_tickangle=30,
            margin=dict(l=40, r=40, t=60, b=120),
        )
        st.plotly_chart(fig_box, use_container_width=True)

        st.subheader("NPS segments by role")
        st.caption(
            "100% stacked bar shows the share of detractors, passives, and promoters in each role.[file:21]"
        )

        nps_ct = pd.crosstab(tmp[role_col], tmp["nps_group"])
        nps_prop = nps_ct.div(nps_ct.sum(axis=1), axis=0).reset_index()
        nps_long = nps_prop.melt(
            id_vars=role_col, var_name="NPS group", value_name="Percent"
        )

        fig_nps_stack = px.bar(
            nps_long,
            x="Percent",
            y=role_col,
            color="NPS group",
            orientation="h",
            barmode="stack",
            labels={"Percent": "Share of respondents"},
            color_discrete_map={
                "Detractor (0–6)": "#d73027",
                "Passive (7–8)": "#fee08b",
                "Promoter (9–10)": "#1a9850",
            },
            template=PLOTLY_TEMPLATE,
        )
        fig_nps_stack.update_layout(
            xaxis_tickformat=".0%",
            margin=dict(l=250, r=40, t=60, b=40),
        )
        st.plotly_chart(fig_nps_stack, use_container_width=True)

    st.markdown("---")

    # ----------------------
    # Ethnicity & recommendation (simplified)
    # ----------------------
    st.header("Recommendation by identity")
    st.caption(
        "Focus on the most common ethnic identities to keep labels readable while still showing equity patterns.[file:21]"
    )

    if total > 0 and filtered_df[ethnicity_col].notna().any() and filtered_df[rec_col].notna().any():
        eth_exploded = filtered_df[[ethnicity_col, rec_col]].dropna().copy()
        eth_exploded = eth_exploded.assign(
            ethnicity_split=eth_exploded[ethnicity_col].astype(str).str.split(",")
        ).explode("ethnicity_split")
        eth_exploded["ethnicity_split"] = eth_exploded["ethnicity_split"].str.strip()
        eth_exploded = eth_exploded[eth_exploded["ethnicity_split"] != ""]

        eth_avg = (
            eth_exploded.groupby("ethnicity_split")[rec_col]
            .mean()
            .reset_index()
        )
        counts = eth_exploded["ethnicity_split"].value_counts().rename("Count").reset_index()
        counts.columns = ["ethnicity_split", "Count"]

        eth_avg = eth_avg.merge(counts, on="ethnicity_split")
        # keep only identities with reasonable sample size; then top 10 by count
        eth_avg = eth_avg[eth_avg["Count"] >= 3]  # tweak threshold as needed
        eth_top = (
            eth_avg.sort_values("Count", ascending=False)
            .head(10)
            .sort_values(rec_col, ascending=True)
        )

        eth_top["eth_wrapped"] = eth_top["ethnicity_split"].apply(lambda x: wrap_label(x, 30))

        st.subheader("Top 10 ethnic identities by recommendation")
        st.caption(
            "Average recommendation score (0–10) for the most common identities (sample ≥ 3 respondents).[file:21]"
        )

        fig_eth = px.bar(
            eth_top,
            x=rec_col,
            y="eth_wrapped",
            orientation="h",
            text=rec_col,
            color_discrete_sequence=SECONDARY_SEQ,
            template=PLOTLY_TEMPLATE,
        )
        fig_eth.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_eth.update_layout(
            margin=dict(l=250, r=40, t=60, b=40),
            yaxis=dict(automargin=True),
            xaxis_title="Average recommendation (0–10)",
            yaxis_title="Ethnic identity",
        )
        st.plotly_chart(fig_eth, use_container_width=True)
    else:
        st.info("Not enough ethnicity and recommendation data to show a stable chart for the selected filters.")

    st.markdown("---")

    # ----------------------
    # Recognition & growth: Likert 100% stacked (by role)
    # ----------------------
    st.header("Recognition and growth perceptions")
    st.caption(
        "Agreement-style questions are best shown as 100% stacked bars, ordered from negative to positive responses.[file:21]"
    )

    # Recognition categories ordered from negative to positive
    recog_order = [
        "I don't feel recognized and acknowledged but I prefer it that way",
        "I don't feel recognized and acknowledged and would prefer staff successes to be highlighted",
        "I do find myself being recognized and acknowledged, but it's rare given the contributions I make",
        "I somewhat feel recognized and acknowledged",
        "Yes, I do feel recognized and acknowledged",
    ]

    growth_order = [
        "I am not interested in career growth and prefer to remain in my current role",
        "Potential to grow seems limited at Homes First and I will likely need to advance my career with another organization",
        "There is very little potential to grow at Homes First",
        "There is some potential to grow and I hope to advance my career with Homes First",
        "Yes, I do feel there is potential to grow at Homes First",
    ]

    col_left, col_right = st.columns(2)

    # Recognition Likert bar
    with col_left:
        st.subheader("Recognition (Likert) by role")
        st.caption(
            "Each bar sums to 100% and shows how recognized staff feel within each role.[file:21]"
        )

        if total > 0 and filtered_df[role_col].notna().any() and filtered_df[recog_col].notna().any():
            rec = filtered_df[[role_col, recog_col]].dropna().copy()
            rec[recog_col] = pd.Categorical(rec[recog_col], categories=recog_order, ordered=True)

            rec_ct = pd.crosstab(rec[role_col], rec[recog_col])
            # keep only columns actually present
            present_rec_cols = [c for c in recog_order if c in rec_ct.columns]
            rec_ct = rec_ct[present_rec_cols]

            rec_prop = rec_ct.div(rec_ct.sum(axis=1), axis=0).reset_index()
            rec_long = rec_prop.melt(
                id_vars=role_col, var_name="Recognition", value_name="Percent"
            )

            fig_rec_likert = px.bar(
                rec_long,
                x="Percent",
                y=role_col,
                color="Recognition",
                orientation="h",
                barmode="stack",
                labels={"Percent": "Share of respondents"},
                color_discrete_sequence=px.colors.sequential.Viridis,
                template=PLOTLY_TEMPLATE,
            )
            fig_rec_likert.update_layout(
                xaxis_tickformat=".0%",
                margin=dict(l=250, r=40, t=60, b=40),
                yaxis=dict(automargin=True),
            )
            st.plotly_chart(fig_rec_likert, use_container_width=True)
        else:
            st.info("No recognition data for the current filters.")

    # Growth Likert bar
    with col_right:
        st.subheader("Growth potential (Likert) by role")
        st.caption(
            "Each bar sums to 100% and shows how staff perceive growth opportunities in each role.[file:21]"
        )

        if total > 0 and filtered_df[role_col].notna().any() and filtered_df[growth_col].notna().any():
            gr = filtered_df[[role_col, growth_col]].dropna().copy()
            gr[growth_col] = pd.Categorical(gr[growth_col], categories=growth_order, ordered=True)

            gr_ct = pd.crosstab(gr[role_col], gr[growth_col])
            present_gr_cols = [c for c in growth_order if c in gr_ct.columns]
            gr_ct = gr_ct[present_gr_cols]

            gr_prop = gr_ct.div(gr_ct.sum(axis=1), axis=0).reset_index()
            gr_long = gr_prop.melt(
                id_vars=role_col, var_name="Growth perception", value_name="Percent"
            )

            fig_gr_likert = px.bar(
                gr_long,
                x="Percent",
                y=role_col,
                color="Growth perception",
                orientation="h",
                barmode="stack",
                labels={"Percent": "Share of respondents"},
                color_discrete_sequence=px.colors.sequential.Plasma,
                template=PLOTLY_TEMPLATE,
            )
            fig_gr_likert.update_layout(
                xaxis_tickformat=".0%",
                margin=dict(l=250, r=40, t=60, b=40),
                yaxis=dict(automargin=True),
            )
            st.plotly_chart(fig_gr_likert, use_container_width=True)
        else:
            st.info("No growth data for the current filters.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Cross-Analysis Dashboard – Likert & NPS view**")

except FileNotFoundError:
    st.error("❌ File not found: 'Combined- Cross Analysis.xlsx'")
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
