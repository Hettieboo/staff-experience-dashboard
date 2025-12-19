import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
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
    .metric-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .metric-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .metric-card-orange {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }
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

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel('Combined- Cross Analysis.xlsx')
    df.columns = [
        'Role',
        'Ethnicity',
        'Disability',
        'Work_Fulfillment',
        'Recommendation_Score',
        'Recognition',
        'Growth_Potential'
    ]
    return df

try:
    df = load_data()

    # Header
    st.title("📊 Employee Survey Cross-Analysis Dashboard")
    st.markdown("### Comparing Employee Groups Across Survey Questions")

    # Sidebar filters
    st.sidebar.header("🔍 Filter Data")
    roles = ['All'] + sorted(df['Role'].dropna().unique().tolist())
    selected_role = st.sidebar.selectbox("Role/Department", roles)

    ethnicities = ['All'] + sorted(df['Ethnicity'].dropna().unique().tolist())
    selected_ethnicity = st.sidebar.selectbox("Ethnicity", ethnicities)

    filtered_df = df.copy()
    if selected_role != 'All':
        filtered_df = filtered_df[filtered_df['Role'] == selected_role]
    if selected_ethnicity != 'All':
        filtered_df = filtered_df[filtered_df['Ethnicity'] == selected_ethnicity]

    total = len(filtered_df)

    # =====================
    # Key metrics
    # =====================
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Responses</div>
                <div class="metric-value">{total}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        avg_score = filtered_df['Recommendation_Score'].mean() if total > 0 else 0
        st.markdown(f"""
            <div class="metric-card metric-card-blue">
                <div class="metric-label">Avg Recommendation</div>
                <div class="metric-value">{avg_score:.1f}/10</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        if total > 0:
            promoters = len(filtered_df[filtered_df['Recommendation_Score'] >= 9])
            detractors = len(filtered_df[filtered_df['Recommendation_Score'] <= 6])
            nps = (promoters - detractors) / total * 100
        else:
            promoters = detractors = nps = 0

        nps_color = "metric-card-green" if nps > 20 else "metric-card-orange" if nps > 0 else "metric-card"
        st.markdown(f"""
            <div class="metric-card {nps_color}">
                <div class="metric-label">NPS Score</div>
                <div class="metric-value">{nps:.0f}</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        if total > 0:
            fulfilled = len(filtered_df[
                filtered_df['Work_Fulfillment'].astype(str).str.contains('extremely', case=False, na=False)
            ])
            pct = fulfilled / total * 100
        else:
            pct = 0
        st.markdown(f"""
            <div class="metric-card metric-card-green">
                <div class="metric-label">Highly Fulfilled</div>
                <div class="metric-value">{pct:.0f}%</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # =====================
    # SECTION 1 – Recommendation score
    # =====================
    st.markdown("## 🎯 Recommendation Score Across Groups")

    if total > 0 and filtered_df['Recommendation_Score'].notna().any():
        # 1A. Horizontal bar: distribution 0–10
        rec_dist = (
            filtered_df['Recommendation_Score']
            .dropna()
            .astype(int)
            .value_counts()
            .sort_index()
            .reset_index()
        )
        rec_dist.columns = ['Score', 'Count']
        rec_dist['NPS_Group'] = pd.cut(
            rec_dist['Score'],
            bins=[-1, 6, 8, 10],
            labels=['Detractor (0–6)', 'Passive (7–8)', 'Promoter (9–10)']
        )

        col_rec1, col_rec2 = st.columns(2)

        with col_rec1:
            fig_rec_dist = px.bar(
                rec_dist,
                y='Score',
                x='Count',
                color='NPS_Group',
                orientation='h',
                color_discrete_map={
                    'Detractor (0–6)': '#d73027',
                    'Passive (7–8)': '#fee08b',
                    'Promoter (9–10)': '#1a9850'
                },
                labels={'Count': 'Number of responses'},
                title='Recommendation Score Distribution (0–10)'
            )
            fig_rec_dist.update_layout(
                margin=dict(l=80, r=40, t=60, b=40),
                showlegend=True
            )
            st.plotly_chart(fig_rec_dist, use_container_width=True)

        with col_rec2:
            # Donut: overall NPS mix
            nps_mix = rec_dist.groupby('NPS_Group')['Count'].sum().reset_index()
            nps_mix = nps_mix[nps_mix['NPS_Group'].notna()]
            fig_nps_donut = px.pie(
                nps_mix,
                names='NPS_Group',
                values='Count',
                hole=0.5,
                color='NPS_Group',
                color_discrete_map={
                    'Detractor (0–6)': '#d73027',
                    'Passive (7–8)': '#fee08b',
                    'Promoter (9–10)': '#1a9850'
                },
                title='Overall NPS Mix'
            )
            fig_nps_donut.update_traces(textposition="inside", textinfo="percent+label")
            fig_nps_donut.update_layout(margin=dict(l=40, r=40, t=60, b=40))
            st.plotly_chart(fig_nps_donut, use_container_width=True)

        # 1B. Horizontal stacked bar: NPS by Role (Top 8 roles)
        st.markdown("### NPS Segments by Role")

        tmp = filtered_df[['Role', 'Recommendation_Score']].dropna().copy()
        tmp['NPS_Group'] = pd.cut(
            tmp['Recommendation_Score'].astype(int),
            bins=[-1, 6, 8, 10],
            labels=['Detractor (0–6)', 'Passive (7–8)', 'Promoter (9–10)']
        )

        top_roles = tmp['Role'].value_counts().head(8).index
        tmp_top = tmp[tmp['Role'].isin(top_roles)]

        nps_ct = pd.crosstab(tmp_top['Role'], tmp_top['NPS_Group'])
        nps_prop = nps_ct.div(nps_ct.sum(axis=1), axis=0).reset_index()
        nps_long = nps_prop.melt(id_vars='Role', var_name='NPS_Group', value_name='Percent')

        fig_nps_role = px.bar(
            nps_long,
            x='Percent',
            y='Role',
            color='NPS_Group',
            orientation='h',
            barmode='stack',
            labels={'Percent': 'Share of respondents'},
            color_discrete_map={
                'Detractor (0–6)': '#d73027',
                'Passive (7–8)': '#fee08b',
                'Promoter (9–10)': '#1a9850'
            },
            title='NPS Segments by Role (Top 8 Roles)'
        )
        fig_nps_role.update_layout(
            xaxis_tickformat=".0%",
            margin=dict(l=250, r=40, t=60, b=40),
            yaxis=dict(automargin=True)
        )
        st.plotly_chart(fig_nps_role, use_container_width=True)

    else:
        st.info("No recommendation data for the current filters.")

    st.markdown("---")

    # =====================
    # SECTION 2 – Work fulfillment (100% stacked bar)
    # =====================
    st.markdown("## 💼 Work Fulfillment Across Roles")

    if total > 0 and filtered_df['Work_Fulfillment'].notna().any():
        top_roles_f = df['Role'].value_counts().head(8).index
        role_fulfill = df[df['Role'].isin(top_roles_f)].copy()

        fulfill_cross = pd.crosstab(
            role_fulfill['Role'],
            role_fulfill['Work_Fulfillment'],
            normalize='index'
        ) * 100

        fulfill_long = fulfill_cross.reset_index().melt(
            id_vars='Role',
            var_name='Fulfillment_Level',
            value_name='Percent'
        )

        fig_fulfill = px.bar(
            fulfill_long,
            x='Percent',
            y='Role',
            color='Fulfillment_Level',
            orientation='h',
            barmode='stack',
            title="Work Fulfillment Distribution by Role (%)",
            labels={'Percent': 'Percentage'}
        )
        fig_fulfill.update_layout(
            xaxis_tickformat=".0%",
            margin=dict(l=250, r=40, t=60, b=40),
            yaxis=dict(automargin=True),
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_fulfill, use_container_width=True)
    else:
        st.info("No work fulfillment data for the current filters.")

    st.markdown("---")

    # =====================
    # SECTION 3 – Recognition & Growth (Likert-style stacked bars)
    # =====================
    st.markdown("## 🌟 Recognition & Growth Sentiment Across Roles")

    # Recognition mapping to shorter labels
    recog_map = {
        "Yes, I do feel recognized and acknowledged": "Yes",
        "I somewhat feel recognized and acknowledged": "Somewhat",
        "I do find myself being recognized and acknowledged, but it's rare given the contributions I make": "Rare",
        "I don't feel recognized and acknowledged and would prefer staff successes to be highlighted more frequently": "No (Want more)",
        "I don't feel recognized and acknowledged but I prefer it that way": "No (Prefer)"
    }

    growth_map = {
        "Yes, I do feel there is potential to grow and I hope to advance my career with Homes First": "Yes",
        "There is some potential to grow and I hope to advance my career with Homes First": "Some",
        "Potential to grow seems limited at Homes First and I will likely need to advance my career with another organization": "Limited",
        "There is very little potential to grow although I would like to advance my career with Homes First": "Very limited",
        "I am not interested in career growth and prefer to remain in my current role": "Not interested"
    }

    col_rg1, col_rg2 = st.columns(2)

    # 3A. Recognition distribution by role – 100% stacked bar
    with col_rg1:
        st.markdown("### Recognition by Role")

        if df['Recognition'].notna().any():
            df_recog = df.copy()
            df_recog['Recognition_Short'] = df_recog['Recognition'].map(recog_map).fillna('Other')

            roles_rg = df_recog['Role'].value_counts().head(8).index
            role_recog = df_recog[df_recog['Role'].isin(roles_rg)]

            recog_cross = pd.crosstab(
                role_recog['Role'],
                role_recog['Recognition_Short'],
                normalize='index'
            ) * 100

            recog_long = recog_cross.reset_index().melt(
                id_vars='Role',
                var_name='Recognition_Level',
                value_name='Percent'
            )

            fig_recog = px.bar(
                recog_long,
                x='Percent',
                y='Role',
                color='Recognition_Level',
                orientation='h',
                barmode='stack',
                labels={'Percent': 'Percentage'},
                title="Recognition Distribution by Role (%)"
            )
            fig_recog.update_layout(
                xaxis_tickformat=".0%",
                margin=dict(l=250, r=40, t=60, b=40),
                yaxis=dict(automargin=True),
                legend=dict(orientation="h", yanchor="bottom", y=1.02,
                            xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_recog, use_container_width=True)
        else:
            st.info("No recognition data available.")

    # 3B. Growth perception by role – 100% stacked bar
    with col_rg2:
        st.markdown("### Growth Potential by Role")

        if df['Growth_Potential'].notna().any():
            df_growth = df.copy()
            df_growth['Growth_Short'] = df_growth['Growth_Potential'].map(growth_map).fillna('Other')

            roles_gr = df_growth['Role'].value_counts().head(8).index
            role_growth = df_growth[df_growth['Role'].isin(roles_gr)]

            growth_cross = pd.crosstab(
                role_growth['Role'],
                role_growth['Growth_Short'],
                normalize='index'
            ) * 100

            growth_long = growth_cross.reset_index().melt(
                id_vars='Role',
                var_name='Growth_Level',
                value_name='Percent'
            )

            fig_growth = px.bar(
                growth_long,
                x='Percent',
                y='Role',
                color='Growth_Level',
                orientation='h',
                barmode='stack',
                labels={'Percent': 'Percentage'},
                title="Growth Potential Distribution by Role (%)"
            )
            fig_growth.update_layout(
                xaxis_tickformat=".0%",
                margin=dict(l=250, r=40, t=60, b=40),
                yaxis=dict(automargin=True),
                legend=dict(orientation="h", yanchor="bottom", y=1.02,
                            xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_growth, use_container_width=True)
        else:
            st.info("No growth perception data available.")

    st.markdown("---")

    # =====================
    # SECTION 4 – Disability comparison (simple horizontal bars)
    # =====================
    st.markdown("## ♿ Disability Status – Key Metrics")

    if df['Disability'].notna().any():
        dis_summary = []
        dis_values = df['Disability'].value_counts().head(6).index

        for dis in dis_values:
            sub = df[df['Disability'] == dis]
            if len(sub) < 3:
                continue

            dis_short = (
                'No disability' if 'do not identify' in dis
                else 'Mental health' if 'Mental health' in dis
                else 'Mobility' if 'Mobility' in dis
                else 'Other' if 'Other' in dis
                else dis[:25]
            )

            avg_score = sub['Recommendation_Score'].mean()
            fulfilled_pct = (
                len(sub[sub['Work_Fulfillment'].astype(str).str.contains('extremely', case=False, na=False)])
                / len(sub) * 100
            )
            recognized_pct = (
                len(sub[sub['Recognition'].astype(str).str.contains('Yes, I do feel recognized', na=False)])
                / len(sub) * 100
            )
            growth_pct = (
                len(sub[sub['Growth_Potential'].astype(str).str.contains('Yes, I do feel there is potential', na=False)])
                / len(sub) * 100
            )

            dis_summary.append({
                'Disability_Short': dis_short,
                'Avg_Recommendation': avg_score,
                'Highly_Fulfilled_%': fulfilled_pct,
                'Feel_Recognized_%': recognized_pct,
                'See_Growth_%': growth_pct,
                'Count': len(sub)
            })

        if dis_summary:
            dis_df = pd.DataFrame(dis_summary).sort_values('Avg_Recommendation', ascending=True)

            st.markdown("### Average Recommendation Score by Disability Status")
            fig_dis_score = px.bar(
                dis_df,
                x='Avg_Recommendation',
                y='Disability_Short',
                orientation='h',
                text='Avg_Recommendation',
                title='Average Recommendation Score by Disability Status'
            )
            fig_dis_score.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig_dis_score.update_layout(
                xaxis_range=[0, 10.5],
                margin=dict(l=200, r=40, t=60, b=40),
                yaxis=dict(automargin=True)
            )
            st.plotly_chart(fig_dis_score, use_container_width=True)

            st.markdown("### Key Experience Metrics by Disability Status")
            # melt the percentages into long form for a stacked horizontal bar
            perc_cols = ['Highly_Fulfilled_%', 'Feel_Recognized_%', 'See_Growth_%']
            dis_long = dis_df.melt(
                id_vars='Disability_Short',
                value_vars=perc_cols,
                var_name='Metric',
                value_name='Percent'
            )

            metric_labels = {
                'Highly_Fulfilled_%': 'Highly fulfilled',
                'Feel_Recognized_%': 'Feel recognized',
                'See_Growth_%': 'See growth potential'
            }
            dis_long['Metric_Label'] = dis_long['Metric'].map(metric_labels)

            fig_dis_perc = px.bar(
                dis_long,
                x='Percent',
                y='Disability_Short',
                color='Metric_Label',
                orientation='h',
                barmode='group',
                title='Experience Metrics by Disability Status',
                labels={'Percent': 'Percentage'}
            )
            fig_dis_perc.update_layout(
                xaxis_tickformat=".0f",
                margin=dict(l=200, r=40, t=60, b=40),
                yaxis=dict(automargin=True),
                legend=dict(orientation="h", yanchor="bottom", y=1.02,
                            xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_dis_perc, use_container_width=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Cross-Analysis Dashboard – Bar & Donut layout**")

except FileNotFoundError:
    st.error("❌ File not found: 'Combined- Cross Analysis.xlsx'")
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
