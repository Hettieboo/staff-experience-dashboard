import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Page config
st.set_page_config(page_title="Homes First Survey Dashboard", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .insight-card {
        background: #f0f7ff;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .insight-positive {
        background: #f0fff4;
        border-left: 4px solid #48bb78;
    }
    .insight-negative {
        background: #fff5f5;
        border-left: 4px solid #f56565;
    }
    .insight-neutral {
        background: #fffaf0;
        border-left: 4px solid #ed8936;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel('Combined- Cross Analysis.xlsx')
    # Rename columns for easier use
    df.columns = ['Role', 'Ethnicity', 'Disability', 'Work_Fulfillment',
                  'Recommendation_Score', 'Recognition', 'Growth_Potential']
    return df

df = load_data()

# Title
st.markdown('<div class="main-title">Homes First Employee Survey Dashboard</div>', unsafe_allow_html=True)

# Sidebar filters
st.sidebar.header("Filters")

roles = ['All'] + sorted(df['Role'].dropna().unique().tolist())
role_filter = st.sidebar.selectbox("Role", roles)

ethnicities = ['All'] + sorted(df['Ethnicity'].dropna().unique().tolist())
ethnicity_filter = st.sidebar.selectbox("Ethnicity", ethnicities)

disabilities = ['All'] + sorted(df['Disability'].dropna().unique().tolist())
disability_filter = st.sidebar.selectbox("Disability", disabilities)

# Apply filters
filtered_df = df.copy()
if role_filter != 'All':
    filtered_df = filtered_df[filtered_df['Role'] == role_filter]
if ethnicity_filter != 'All':
    filtered_df = filtered_df[filtered_df['Ethnicity'] == ethnicity_filter]
if disability_filter != 'All':
    filtered_df = filtered_df[filtered_df['Disability'] == disability_filter]

# Helper function for score bands
def get_score_band(score):
    if pd.isna(score):
        return np.nan
    if score <= 3:
        return '0–3'
    elif score <= 6:
        return '4–6'
    elif score <= 8:
        return '7–8'
    else:
        return '9–10'

filtered_df['Score_Band'] = filtered_df['Recommendation_Score'].apply(get_score_band)

# Helper function to create disability categories
def categorize_disability(disability_text):
    if isinstance(disability_text, float) and np.isnan(disability_text):
        return 'Unknown'
    text = str(disability_text).lower()
    if 'do not identify' in text:
        return 'No Disability'
    elif 'prefer not to specify' in text:
        return 'Prefer Not to Specify'
    else:
        return 'With Disability'

df['Disability_Category'] = df['Disability'].apply(categorize_disability)
filtered_df['Disability_Category'] = filtered_df['Disability'].apply(categorize_disability)

# ============= KEY INSIGHTS SECTION =============
st.markdown("## 🔍 Key Insights & Patterns")

overall_avg = df['Recommendation_Score'].mean()

# Insight 1: Disability impact
disability_scores = df.groupby('Disability_Category')['Recommendation_Score'].agg(['mean', 'count']).round(2)
disability_scores = disability_scores[disability_scores['count'] >= 5]

# Insight 2: Role with lowest / highest scores (5+ responses)
role_scores = df.groupby('Role')['Recommendation_Score'].agg(['mean', 'count']).round(2)
role_scores = role_scores[role_scores['count'] >= 5]
lowest_role = role_scores['mean'].idxmin() if len(role_scores) > 0 else None
highest_role = role_scores['mean'].idxmax() if len(role_scores) > 0 else None

# Insight 3: Extremely fulfilling correlation
extremely_fulfilling = df[df['Work_Fulfillment'].str.contains('extremely', case=False, na=False)]
avg_score_extremely = extremely_fulfilling['Recommendation_Score'].mean()
not_extremely = df[~df['Work_Fulfillment'].str.contains('extremely', case=False, na=False)]
avg_score_not_extremely = not_extremely['Recommendation_Score'].mean()

# Insight 4: Recognition impact
recognized = df[df['Recognition'].str.contains('Yes, I do feel recognized', case=False, na=False)]
avg_recognized = recognized['Recommendation_Score'].mean()
not_recognized = df[df['Recognition'].str.contains("don't feel recognized and would prefer", case=False, na=False)]
avg_not_recognized = not_recognized['Recommendation_Score'].mean() if len(not_recognized) > 0 else 0

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Overall Patterns")

    diff_fulfillment = avg_score_extremely - avg_score_not_extremely
    if not np.isnan(diff_fulfillment) and diff_fulfillment > 2:
        st.markdown(f"""
        <div class="insight-card insight-positive">
            <strong>✅ Strong Positive Link:</strong> Employees who find work "extremely fulfilling"
            score <strong>{diff_fulfillment:.1f} points higher</strong>
            ({avg_score_extremely:.1f} vs {avg_score_not_extremely:.1f}) on recommendation.
        </div>
        """, unsafe_allow_html=True)

    if avg_not_recognized > 0:
        diff_recognition = avg_recognized - avg_not_recognized
        if abs(diff_recognition) > 1.5:
            insight_class = "insight-positive" if diff_recognition > 0 else "insight-negative"
            icon = "✅" if diff_recognition > 0 else "⚠️"
            direction = "higher" if diff_recognition > 0 else "lower"
            st.markdown(f"""
            <div class="insight-card {insight_class}">
                <strong>{icon} Recognition Impact:</strong>
                Employees who feel recognized score <strong>{abs(diff_recognition):.1f} points {direction}</strong>
                ({avg_recognized:.1f} vs {avg_not_recognized:.1f}).
            </div>
            """, unsafe_allow_html=True)

    if lowest_role is not None:
        st.markdown(f"""
        <div class="insight-card insight-negative">
            <strong>⚠️ Lowest Scoring Role:</strong> {lowest_role}
            (avg: {role_scores.loc[lowest_role, 'mean']:.1f}, n={int(role_scores.loc[lowest_role, 'count'])})
        </div>
        """, unsafe_allow_html=True)

    if highest_role is not None:
        st.markdown(f"""
        <div class="insight-card insight-positive">
            <strong>✅ Highest Scoring Role:</strong> {highest_role}
            (avg: {role_scores.loc[highest_role, 'mean']:.1f}, n={int(role_scores.loc[highest_role, 'count'])})
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("### 👥 Demographic Patterns")

    if {'With Disability', 'No Disability'} <= set(disability_scores.index):
        diff_disability = (
            disability_scores.loc['No Disability', 'mean']
            - disability_scores.loc['With Disability', 'mean']
        )
        if abs(diff_disability) > 1:
            insight_class = "insight-negative" if diff_disability > 0 else "insight-positive"
            icon = "⚠️" if diff_disability > 0 else "✅"
            st.markdown(f"""
            <div class="insight-card {insight_class}">
                <strong>{icon} Disability Status:</strong>
                Employees with disabilities score
                <strong>{abs(diff_disability):.1f} points lower</strong>
                on average compared to those without disabilities
                ({disability_scores.loc['With Disability', 'mean']:.1f} vs
                {disability_scores.loc['No Disability', 'mean']:.1f}).
            </div>
            """, unsafe_allow_html=True)

    ethnicity_scores = df.groupby('Ethnicity')['Recommendation_Score'].agg(['mean', 'count']).round(2)
    ethnicity_scores = ethnicity_scores[ethnicity_scores['count'] >= 5]
    if len(ethnicity_scores) > 0:
        top_ethnicity = ethnicity_scores['mean'].idxmax()
        top_ethnicity_short = top_ethnicity.split('(')[0].strip() if '(' in top_ethnicity else top_ethnicity[:40]
        st.markdown(f"""
        <div class="insight-card insight-positive">
            <strong>✅ Highest Scoring Ethnicity:</strong> {top_ethnicity_short}
            (avg: {ethnicity_scores.loc[top_ethnicity, 'mean']:.1f}, n={int(ethnicity_scores.loc[top_ethnicity, 'count'])})
        </div>
        """, unsafe_allow_html=True)

    low_scores = df[df['Recommendation_Score'] <= 4]
    if len(low_scores) > 0:
        low_score_roles = low_scores['Role'].value_counts().head(1)
        st.markdown(f"""
        <div class="insight-card insight-neutral">
            <strong>📌 Low Score Concentration:</strong> {low_score_roles.index[0]} has
            {low_score_roles.values[0]} responses with scores ≤4.
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Metric cards (filtered)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{len(filtered_df)}</div>
        <div class="metric-label">Total Responses (filtered)</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    avg_score_f = filtered_df['Recommendation_Score'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{avg_score_f:.1f}</div>
        <div class="metric-label">Avg Recommendation Score</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    low_scores_f = len(filtered_df[filtered_df['Recommendation_Score'] <= 4])
    high_scores_f = len(filtered_df[filtered_df['Recommendation_Score'] >= 8])
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{low_scores_f} / {high_scores_f}</div>
        <div class="metric-label">Low (≤4) / High (≥8) Scores</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    extremely_fulfilling_f = len(
        filtered_df[
            filtered_df['Work_Fulfillment'].str.contains('extremely', case=False, na=False)
        ]
    )
    pct_extremely_f = (extremely_fulfilling_f / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{pct_extremely_f:.1f}%</div>
        <div class="metric-label">"Extremely" Fulfilling (filtered)</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ========= Helper functions for stacked bars =========
def shorten_role(role):
    mapping = {
        'Director/Assistant Director/Manager/Assistant Manager (HR/Finance/Property/Fundraising/Development)': 'Director/Manager (HR/Finance/Dev)',
        'Director/Assistant Director/Manager/Assistant Manager/Site Manager (Shelters/Housing)': 'Director/Manager (Shelters)',
        'Supervisor (Shelters/Housing)': 'Supervisor (Shelters)',
        'Supervisor (HR/Finance/Property/Fundraising/Development)': 'Supervisor (HR/Finance/Dev)',
        'ICM - Shelters (includes ICM, HHW, Community Engagement, ICM Health Standards, etc.)': 'ICM - Shelters',
        'Non-24 Hour Program (including ICM, follow-up supports and PSW)': 'Non-24 Hour Program',
        'Other (Smaller departments/teams not listed seperately in an effort to maintain confidentiality)': 'Other',
        'Prefer not to disclose/Other': 'Prefer not to disclose',
    }
    return mapping.get(role, role)

def shorten_text(text, max_length=60):
    if not isinstance(text, str):
        return text
    return text if len(text) <= max_length else text[:max_length-3] + '...'

def create_stacked_bar(df_in, question_col, title, top_n=8):
    sub = df_in[['Role', question_col]].dropna().copy()
    if sub.empty:
        st.info(f"No data for {title} with current filters.")
        return

    # Top roles by count
    top_roles = sub['Role'].value_counts().head(top_n).index.tolist()
    sub = sub[sub['Role'].isin(top_roles)]

    sub['Role_Short'] = sub['Role'].apply(shorten_role)
    # Crosstab in row percentages
    tab = pd.crosstab(sub['Role_Short'], sub[question_col], normalize='index') * 100

    long_df = tab.reset_index().melt(
        id_vars='Role_Short', var_name='Answer', value_name='Percent'
    )
    long_df['Answer_Short'] = long_df['Answer'].apply(lambda x: shorten_text(str(x), 40))

    height = max(400, 45 * tab.shape[0] + 120)
    colors = px.colors.qualitative.Set3

    fig = px.bar(
        long_df,
        x='Percent',
        y='Role_Short',
        color='Answer_Short',
        orientation='h',
        barmode='stack',
        labels={'Percent': 'Percentage of respondents', 'Role_Short': 'Role'},
        title=title,
        color_discrete_sequence=colors
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
        margin=dict(l=260, r=40, t=80, b=90),
    )
    st.plotly_chart(fig, use_container_width=True)

# ========= QUESTION BREAKDOWN SECTION =========
st.markdown("## 📊 Question Breakdown by Department")

# Recommendation – main distribution and bands by role
st.subheader("How likely are you to recommend Homes First as a good place to work?")

if len(filtered_df) > 0 and filtered_df['Recommendation_Score'].notna().any():
    # Overall distribution (horizontal bar)
    rec_counts = (
        filtered_df['Recommendation_Score']
        .dropna()
        .astype(int)
        .value_counts()
        .sort_index()
        .reset_index()
    )
    rec_counts.columns = ['Score', 'Count']

    col_rec1, col_rec2 = st.columns(2)

    with col_rec1:
        fig_rec = px.bar(
            rec_counts,
            y='Score',
            x='Count',
            orientation='h',
            labels={'Count': 'Number of respondents'},
            title='Score distribution (0–10)'
        )
        fig_rec.update_layout(margin=dict(l=80, r=40, t=60, b=40))
        st.plotly_chart(fig_rec, use_container_width=True)

    with col_rec2:
        rec_counts['Band'] = rec_counts['Score'].apply(get_score_band)
        band_counts = rec_counts.groupby('Band')['Count'].sum().reset_index()
        band_counts = band_counts[band_counts['Band'].notna()]

        if not band_counts.empty:
            fig_donut = px.pie(
                band_counts,
                names='Band',
                values='Count',
                hole=0.5,
                title='Score bands (0–3, 4–6, 7–8, 9–10)'
            )
            fig_donut.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("Not enough data to show score bands for current filters.")

    st.subheader("Score bands by role (%)")
    if filtered_df['Score_Band'].notna().any():
        create_stacked_bar(filtered_df, 'Score_Band', 'Recommendation score bands by role (%)')
    else:
        st.info("No score band data for current filters.")
else:
    st.info("No recommendation data for current filters.")

st.markdown("---")

# Work Fulfillment
st.subheader("How fulfilling and rewarding do you find your work?")
create_stacked_bar(filtered_df, 'Work_Fulfillment', 'Work fulfillment distribution by role (%)')

st.markdown("---")

# Recognition
st.subheader("Do you feel you get acknowledged and recognized for your contribution at work?")
create_stacked_bar(filtered_df, 'Recognition', 'Recognition distribution by role (%)')

st.markdown("---")

# Growth Potential
st.subheader("Do you feel there is potential for growth at Homes First?")
create_stacked_bar(filtered_df, 'Growth_Potential', 'Growth potential distribution by role (%)')

st.sidebar.markdown("---")
st.sidebar.markdown("**Homes First Survey Dashboard – v1.0**")
