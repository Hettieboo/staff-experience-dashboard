import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Homes First – Staff Experience Dashboard",
    page_icon="📊",
    layout="wide"
)

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("Combined- Cross Analysis.xlsx")
    df = df.iloc[:, :7]
    df.columns = [
        "Role",
        "Ethnicity",
        "Disability",
        "Work_Fulfillment",
        "Recommendation",
        "Recognition",
        "Growth"
    ]
    return df

df = load_data()

# -------------------------------------------------
# ROLE FILTER
# -------------------------------------------------
target_roles = [
    "Administrator",
    "Coordinator",
    "Prefer not to disclose/other",
    "Generalist",
    "Analyst",
    "Supervisor (Shelters/Housing)",
    "Director/Assistant Director/Manager/Assistant Manager (HR/Finance/Property/Fundraising/Development)",
    "Director/Assistant Director/Manager/Assistant Manager/Site Manager (Shelters/Housing)",
    "Supervisor (HR/Finance/Property/Fundraising/Development)",
    "CSW - Shelters",
    "Non-24 Hour Program (including ICM, follow-up supports and PSW)",
    "Relief",
    "ICM - Shelters (includes ICM, HHW, Community Engagement, ICM Health Standards, etc.)",
    "Other (Smaller departments/teams not listed seperately in an effort to maintain confidentiality)"
]

df = df[df["Role"].isin(target_roles)]

# -------------------------------------------------
# MULTI-SELECT HANDLING
# -------------------------------------------------
df_eth = df.assign(
    Ethnicity=df["Ethnicity"].astype(str).str.split(",")
).explode("Ethnicity")
df_eth["Ethnicity"] = df_eth["Ethnicity"].str.strip()

df_dis = df.assign(
    Disability=df["Disability"].astype(str).str.split(",")
).explode("Disability")
df_dis["Disability"] = df_dis["Disability"].str.strip()

# -------------------------------------------------
# SENTIMENT MAPPING
# -------------------------------------------------
recognition_map = {
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

df["Recognition_Short"] = df["Recognition"].map(recognition_map)
df["Growth_Short"] = df["Growth"].map(growth_map)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title("📊 Homes First – Staff Experience Cross-Analysis")
st.markdown(
    "Professional analysis across role, fulfillment, recommendation, recognition, growth, ethnicity, and disability."
)

# -------------------------------------------------
# KPI METRICS
# -------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Responses", len(df))

with col2:
    st.metric("Avg Recommendation", f"{df['Recommendation'].mean():.1f} / 10")

with col3:
    promoters = (df["Recommendation"] >= 9).sum()
    detractors = (df["Recommendation"] <= 6).sum()
    nps = ((promoters - detractors) / len(df)) * 100
    st.metric("NPS", f"{nps:.0f}")

with col4:
    high_fulfillment = (
        df["Work_Fulfillment"]
        .str.contains("extremely", case=False, na=False)
        .mean() * 100
    )
    st.metric("Highly Fulfilled", f"{high_fulfillment:.0f}%")

st.divider()

# -------------------------------------------------
# WORK FULFILLMENT BY ROLE
# -------------------------------------------------
fulfill_cross = (
    pd.crosstab(df["Role"], df["Work_Fulfillment"], normalize="index") * 100
)

fig_fulfill = px.bar(
    fulfill_cross,
    orientation="h",
    height=650,
    title="Work Fulfillment Distribution by Role (%)"
)

fig_fulfill.update_layout(
    legend_title="Fulfillment Level",
    bargap=0.18
)

st.plotly_chart(fig_fulfill, use_container_width=True)

st.divider()

# -------------------------------------------------
# HEATMAP FUNCTION WITH PROPER CONTRAST
# -------------------------------------------------
def heatmap_with_annotations(df_cross, title):
    z = df_cross.values
    x = df_cross.columns
    y = df_cross.index

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=x,
            y=y,
            colorscale="RdYlGn",
            hovertemplate="%{y}<br>%{x}: %{z:.1f}%<extra></extra>"
        )
    )

    # Dynamic annotations (THIS fixes contrast correctly)
    annotations = []
    for i, role in enumerate(y):
        for j, col in enumerate(x):
            value = z[i][j]
            color = "white" if value >= 45 else "black"
            annotations.append(
                dict(
                    x=col,
                    y=role,
                    text=f"{value:.0f}%",
                    showarrow=False,
                    font=dict(color=color, size=12)
                )
            )

    fig.update_layout(
        title=title,
        annotations=annotations,
        height=680,
        margin=dict(t=120, l=260, r=40, b=40),
        yaxis=dict(autorange="reversed")
    )

    return fig

# -------------------------------------------------
# RECOGNITION & GROWTH HEATMAPS
# -------------------------------------------------
st.markdown("## 🌟 Recognition & Growth Sentiment Across Roles")
st.markdown("<div style='margin-bottom:30px'></div>", unsafe_allow_html=True)

recog_cross = (
    pd.crosstab(df["Role"], df["Recognition_Short"], normalize="index") * 100
)

growth_cross = (
    pd.crosstab(df["Role"], df["Growth_Short"], normalize="index") * 100
)

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(
        heatmap_with_annotations(recog_cross, "Recognition Sentiment by Role (%)"),
        use_container_width=True
    )

with col2:
    st.plotly_chart(
        heatmap_with_annotations(growth_cross, "Growth Perception by Role (%)"),
        use_container_width=True
    )

st.divider()

# -------------------------------------------------
# ETHNICITY BY ROLE
# -------------------------------------------------
eth_cross = (
    pd.crosstab(df_eth["Role"], df_eth["Ethnicity"], normalize="index") * 100
)

fig_eth = px.bar(
    eth_cross,
    orientation="h",
    height=750,
    title="Ethnic / Racial Identity Distribution by Role (%)"
)

fig_eth.update_layout(
    legend_title="Ethnicity",
    bargap=0.22
)

st.plotly_chart(fig_eth, use_container_width=True)

st.divider()

# -------------------------------------------------
# DISABILITY BY ROLE
# -------------------------------------------------
dis_cross = (
    pd.crosstab(df_dis["Role"], df_dis["Disability"], normalize="index") * 100
)

fig_dis = px.bar(
    dis_cross,
    orientation="h",
    height=750,
    title="Disability Identification by Role (%)"
)

fig_dis.update_layout(
    legend_title="Disability",
    bargap=0.22
)

st.plotly_chart(fig_dis, use_container_width=True)

st.divider()

# -------------------------------------------------
# RECOMMENDATION SCORE BY ROLE
# -------------------------------------------------
rec_role = (
    df.groupby("Role")["Recommendation"]
    .mean()
    .sort_values()
)

fig_rec = px.bar(
    rec_role,
    orientation="h",
    height=650,
    title="Average Recommendation Score by Role",
    labels={"value": "Score (0–10)", "Role": ""}
)

st.plotly_chart(fig_rec, use_container_width=True)
