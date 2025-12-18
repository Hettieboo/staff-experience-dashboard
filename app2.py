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
NEG_POS_SEQ = ["#d73027", "#fc8d59", "#fee08b", "#91cf60", "#1a9850"]

# Helper to wrap long labels for y-axis
def wrap_label(label, width=30):
    if not isinstance(label, str):
        return label
    return "<br>".join(textwrap.wrap(label, width=width))

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
    # Columns from your dataset
    # ----------------------
    role_col = 'Select the role/department that best describes your current position at Homes First.'
    ethnicity_col = 'Which racial or ethnic identity/identities best reflect you. (Select all that apply.)'
    disability_col = 'Do you identify as an individual living with a disability/disabilities and if so, what type of disability/disabilities do you have? (Select all that apply.)'
    work_col = 'How fulfilling and rewarding do you find your work?'
    rec_col = 'How likely are you to recommend Homes First as a good place to work?'
    recog_col = 'Do you feel you get acknowledged and recognized for your contribution  at work?'
    growth_col = 'Do you feel there is potential for growth at Homes First?'

    # ----------------------
    # Sidebar Filters
    # ----------------------
    st.sidebar.header("🔍 Filter Data")
    roles = ['All'] + sorted(df[role_col].dropna().unique().tolist())
    selected_role = st.sidebar.selectbox("Role/Department", roles)

    # explode ethnicity and disability for better filtering
    def split_multi(series):
        return sorted(set(
            e.strip()
            for sublist in series.dropna().astype(str).str.split(',')
            for e in sublist if e.strip()
        ))

    ethnicities = ['All'] + split_multi(df[ethnicity_col])
    selected_ethnicity = st.sidebar.selectbox("Ethnicity", ethnicities)

    disabilities = ['All'] + split_multi(df[disability_col])
    selected_disability = st.sidebar.selectbox("Disability", disabilities)

    filtered_df = df.copy()
    if selected_role != 'All':
        filtered_df = filtered_df[filtered_df[role_col] == selected_role]
    if selected_ethnicity != 'All':
        filtered_df = filtered_df[filtered_df[ethnicity_col].astype(str).str.contains(selected_ethnicity, na=False)]
    if selected_disability != 'All':
        filtered_df = filtered_df[filtered_df[disability_col].astype(str).str.contains(selected_disability, na=False)]

    total = len(filtered_df)

    # ----------------------
    # Title & intro
    # ----------------------
    st.title("📊 Employee Survey Cross-Analysis Dashboard")
    st.markdown("Explore how different employee groups respond across key survey questions such as recommendation, recognition, and growth.[file:21]")

    # ----------------------
    # Key Metrics
    # ----------------------
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"<div class='metric-card'><div class='metric-label'>Total Responses</div><div class='metric-value'>{total}</div></div>",
            unsafe_allow_html=True
        )

    with col2:
        avg_score = filtered_df[rec_col].mean() if total > 0 else 0
        st.markdown(
            f"<div class='metric-card metric-card-blue'><div class='metric-label'>Avg Recommendation</div><div class='metric-value'>{avg_score:.1f}/10</div></div>",
            unsafe_allow_html=True
        )

    with col3:
        promoters = len(filtered_df[filtered_df[rec_col] >= 9]) if total > 0 else 0
        detractors = len(filtered_df[filtered_df[rec_col] <= 6]) if total > 0 else 0
        nps = ((promoters - detractors) / total * 100) if total > 0 else 0
        nps_color = "metric-card-green" if nps > 20 else "metric-card-orange" if nps > 0 else "metric-card"
        st.markdown(
            f"<div class='metric-card {nps_color}'><div class='metric-label'>NPS Score</div><div class='metric-value'>{nps:.0f}</div></div>",
            unsafe_allow_html=True
        )

    with col4:
        fulfilled = len(filtered_df[filtered_df[work_col].astype(str).str.contains('extremely', case=False, na=False)]) if total > 0 else 0
        pct = (fulfilled / total * 100) if total > 0 else 0
        st.markdown(
            f"<div class='metric-card metric-card-green'><div class='metric-label'>Highly Fulfilled</div><div class='metric-value'>{pct:.0f}%</div></div>",
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ----------------------
    # Recommendation behaviour
    # ----------------------
    st.header("Recommendation behaviour")
    st.caption("See how recommendation scores are distributed and how they vary by role and ethnicity.[file:21]")

    # Distribution 0–10
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
            labels=["Detractor (0–6)", "Passive (7–8)", "Promoter (9–10)"]
        )

        st.subheader("Recommendation score distribution")
        st.caption("Breakdown of scores from 0–10 into detractors, passives, and promoters for the selected filters.[file:21]")

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

    # ----------------------
    # Average recommendation by role & ethnicity
    # ----------------------
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Average recommendation by role")
        st.caption("Higher bars indicate groups more likely to recommend Homes First as a place to work.[file:21]")

        if total > 0 and filtered_df[role_col].notna().any():
            role_avg = (
                filtered_df.groupby(role_col)[rec_col]
                .mean()
                .reset_index()
                .sort_values(rec_col, ascending=True)
            )
            role_avg["role_wrapped"] = role_avg[role_col].apply(lambda x: wrap_label(x, 25))
            height = max(400, 40 * len(role_avg) + 150)
            fig_bar = px.bar(
                role_avg,
                x=rec_col,
                y="role_wrapped",
                orientation="h",
                text=rec_col,
                color_discrete_sequence=PRIMARY_SEQ,
                template=PLOTLY_TEMPLATE,
            )
            fig_bar.update_traces(texttemplate="%{text:.1f}", textposition="outside")
            fig_bar.update_layout(
                height=height,
                margin=dict(l=250, r=40, t=60, b=40),
                yaxis=dict(automargin=True),
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No role data for the current filters.")

    with col_b:
        st.subheader("Average recommendation by ethnicity (top 10)")
        st.caption("Top ethnic identities by average likelihood to recommend; long labels are wrapped for readability.[file:21]")

        if total > 0 and filtered_df[ethnicity_col].notna().any():
            # explode multi-ethnicity to treat each component as a row
            eth_exploded = filtered_df.copy()
            eth_exploded = eth_exploded.assign(
                ethnicity_split=eth_exploded[ethnicity_col].astype(str).str.split(',')
            ).explode('ethnicity_split')
            eth_exploded['ethnicity_split'] = eth_exploded['ethnicity_split'].str.strip()
            eth_exploded = eth_exploded[eth_exploded['ethnicity_split'] != ""]

            eth_avg = (
                eth_exploded.groupby('ethnicity_split')[rec_col]
                .mean()
                .reset_index()
                .sort_values(rec_col, ascending=False)
                .head(10)
                .sort_values(rec_col, ascending=True)
            )
            eth_avg["eth_wrapped"] = eth_avg['ethnicity_split'].apply(lambda x: wrap_label(x, 25))

            height = max(400, 40 * len(eth_avg) + 150)
            fig_eth = px.bar(
                eth_avg,
                x=rec_col,
                y="eth_wrapped",
                orientation="h",
                text=rec_col,
                color_discrete_sequence=SECONDARY_SEQ,
                template=PLOTLY_TEMPLATE,
            )
            fig_eth.update_traces(texttemplate="%{text:.1f}", textposition="outside")
            fig_eth.update_layout(
                height=height,
                margin=dict(l=250, r=40, t=60, b=40),
                yaxis=dict(automargin=True),
            )
            st.plotly_chart(fig_eth, use_container_width=True)
        else:
            st.info("No ethnicity data for the current filters.")

    st.markdown("---")

    # ----------------------
    # Recognition and growth by role (stacked bars)
    # ----------------------
    st.header("Recognition and growth")
    st.caption("How recognition and perceived growth potential differ across roles, shown as within-role percentages.[file:21]")

    col_left, col_right = st.columns(2)

    # Order recognition categories from negative to positive if present
    recog_order = [
        "I don't feel recognized and acknowledged but I prefer it that way",
        "I don't feel recognized and acknowledged and would prefer staff successes to be highlighted",
        "I do find myself being recognized and acknowledged, but it's rare given the contributions I make",
        "I somewhat feel recognized and acknowledged",
        "Yes, I do feel recognized and acknowledged"
    ]

    growth_order = [
        "I am not interested in career growth and prefer to remain in my current role",
        "Potential to grow seems limited at Homes First and I will likely need to advance my career with another organization",
        "There is very little potential to grow at Homes First",
        "There is some potential to grow and I hope to advance my career with Homes First",
        "Yes, I do feel there is potential to grow at Homes First"
    ]

    # --- Recognition by role: stacked bar ---
    with col_left:
        st.subheader("Recognition distribution by role")
        st.caption("Each bar sums to 100% and shows how often staff in each role feel recognized.[file:21]")

        if total > 0 and filtered_df[role_col].notna().any() and filtered_df[recog_col].notna().any():
            recog_cross_count = pd.crosstab(filtered_df[role_col], filtered_df[recog_col])
            # enforce category order where possible
            recog_cols = [c for c in recog_order if c in recog_cross_count.columns] + \
                         [c for c in recog_cross_count.columns if c not in recog_order]
            recog_cross_count = recog_cross_count[recog_cols]

            recog_prop = (recog_cross_count.div(recog_cross_count.sum(axis=1), axis=0) * 100).reset_index()
            recog_prop["role_wrapped"] = recog_prop[role_col].apply(lambda x: wrap_label(x, 25))
            recog_long = recog_prop.melt(
                id_vars=[role_col, "role_wrapped"],
                var_name="Recognition",
                value_name="Percent"
            )

            fig_rec_stack = px.bar(
                recog_long,
                x="Percent",
                y="role_wrapped",
                color="Recognition",
                orientation="h",
                barmode="stack",
                color_discrete_sequence=px.colors.sequential.Viridis,
                labels={"Percent": "% of respondents"},
                template=PLOTLY_TEMPLATE,
            )
            fig_rec_stack.update_layout(
                height=max(400, 45 * recog_prop.shape[0] + 150),
                margin=dict(l=250, r=40, t=60, b=40),
                yaxis=dict(automargin=True),
            )
            st.plotly_chart(fig_rec_stack, use_container_width=True)
        else:
            st.info("No recognition data for the current filters.")

    # --- Growth potential by role: stacked bar ---
    with col_right:
        st.subheader("Growth potential by role")
        st.caption("Each bar sums to 100% and shows how staff in each role perceive growth opportunities.[file:21]")

        if total > 0 and filtered_df[role_col].notna().any() and filtered_df[growth_col].notna().any():
            growth_cross_count = pd.crosstab(filtered_df[role_col], filtered_df[growth_col])
            growth_cols = [c for c in growth_order if c in growth_cross_count.columns] + \
                          [c for c in growth_cross_count.columns if c not in growth_order]
            growth_cross_count = growth_cross_count[growth_cols]

            growth_prop = (growth_cross_count.div(growth_cross_count.sum(axis=1), axis=0) * 100).reset_index()
            growth_prop["role_wrapped"] = growth_prop[role_col].apply(lambda x: wrap_label(x, 25))
            growth_long = growth_prop.melt(
                id_vars=[role_col, "role_wrapped"],
                var_name="Growth perception",
                value_name="Percent"
            )

            fig_growth_stack = px.bar(
                growth_long,
                x="Percent",
                y="role_wrapped",
                color="Growth perception",
                orientation="h",
                barmode="stack",
                color_discrete_sequence=px.colors.sequential.Plasma,
                labels={"Percent": "% of respondents"},
                template=PLOTLY_TEMPLATE,
            )
            fig_growth_stack.update_layout(
                height=max(400, 45 * growth_prop.shape[0] + 150),
                margin=dict(l=250, r=40, t=60, b=40),
                yaxis=dict(automargin=True),
            )
            st.plotly_chart(fig_growth_stack, use_container_width=True)
        else:
            st.info("No growth data for the current filters.")

    st.markdown("---")

    # ----------------------
    # Compact heatmap overview (optional, cleaned)
    # ----------------------
    st.header("Heatmap overview by role")
    st.caption("Compact view of how recognition and growth distributions differ across roles.[file:21]")

    # Recognition heatmap
    if total > 0 and filtered_df[role_col].notna().any() and filtered_df[recog_col].notna().any():
        recog_cross = pd.crosstab(filtered_df[role_col], filtered_df[recog_col], normalize='index') * 100
        recog_cross = recog_cross[recog_cross.columns.intersection(recog_cols)]  # same ordering as stacked bar
        fig_heat_rec = go.Figure(go.Heatmap(
            z=recog_cross.values,
            x=[wrap_label(c, 20) for c in recog_cross.columns],
            y=[wrap_label(r, 20) for r in recog_cross.index],
            colorscale='Viridis',
            text=[[f'{v:.0f}%' for v in row] for row in recog_cross.values],
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="%", len=0.8),
            hovertemplate='<b>%{y}</b><br>%{x}: %{z:.1f}%<extra></extra>'
        ))
        fig_heat_rec.update_layout(
            title="Recognition distribution by role (%)",
            xaxis_title="Recognition",
            yaxis_title="Role",
            height=max(400, 40 * len(recog_cross) + 150),
            margin=dict(l=220, r=50, t=80, b=80),
            template=PLOTLY_TEMPLATE,
        )
        st.plotly_chart(fig_heat_rec, use_container_width=True)
    else:
        st.info("No recognition data to show in heatmap for the current filters.")

    # Growth heatmap
    if total > 0 and filtered_df[role_col].notna().any() and filtered_df[growth_col].notna().any():
        growth_cross = pd.crosstab(filtered_df[role_col], filtered_df[growth_col], normalize='index') * 100
        growth_cross = growth_cross[growth_cross.columns.intersection(growth_cols)]
        fig_growth = go.Figure(go.Heatmap(
            z=growth_cross.values,
            x=[wrap_label(c, 20) for c in growth_cross.columns],
            y=[wrap_label(r, 20) for r in growth_cross.index],
            colorscale='Viridis',
            text=[[f'{v:.0f}%' for v in row] for row in growth_cross.values],
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="%", len=0.8),
            hovertemplate='<b>%{y}</b><br>%{x}: %{z:.1f}%<extra></extra>'
        ))
        fig_growth.update_layout(
            title="Growth potential by role (%)",
            xaxis_title="Growth perception",
            yaxis_title="Role",
            height=max(400, 40 * len(growth_cross) + 150),
            margin=dict(l=220, r=50, t=80, b=80),
            template=PLOTLY_TEMPLATE,
        )
        st.plotly_chart(fig_growth, use_container_width=True)
    else:
        st.info("No growth data to show in heatmap for the current filters.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Cross-Analysis Dashboard v4.0**")

except FileNotFoundError:
    st.error("❌ File not found: 'Combined- Cross Analysis.xlsx'")
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
