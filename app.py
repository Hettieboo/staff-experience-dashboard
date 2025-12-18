# ============================
# Streamlit Dashboard: Homes First Survey
# ============================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ----------------------------
# 1. Page Config
# ----------------------------
st.set_page_config(page_title="Homes First Survey Dashboard", layout="wide")

st.title("Homes First Staff Experience Dashboard")
st.markdown("Interactive analysis of staff survey results.")

# ----------------------------
# 2. Load Dataset
# ----------------------------
file_path = 'Combined- Cross Analysis.xlsx'

if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    st.success("Dataset loaded successfully!")
else:
    st.error(f"File not found: {file_path}")
    st.stop()

# ----------------------------
# 3. Clean Multi-select Columns
# ----------------------------
multi_select_cols = [
    'Which racial or ethnic identity/identities best reflect you. (Select all that apply.)',
    'Do you identify as an individual living with a disability/disabilities and if so, what type of disability/disabilities do you have? (Select all that apply.)'
]

for col in multi_select_cols:
    df[col] = df[col].astype(str).str.split(r',|;').apply(lambda x: [i.strip() for i in x] if isinstance(x, list) else [])

# ----------------------------
# 4. Clean Textual Responses
# ----------------------------
# Work Fulfillment
fulfillment_map = {
    "I find the work I do extremely fulfilling and rewarding": "High",
    "I find the work I do fulfilling and rewarding in some parts and not so much in others": "Medium",
    "I find the work I do somewhat fulfilling and rewarding": "Medium",
    "I don't find the work I do to be fulfilling or rewarding but I like other aspects of the job (such as the hours, the location, the pay/benefits, etc.)": "Low",
    "I don't find the work I do to be fulfilling or rewarding so I am taking steps to change jobs/career path/industry": "Low"
}
df['Work_Fulfillment_Clean'] = df['How fulfilling and rewarding do you find your work?'].map(fulfillment_map).fillna('Unknown')

# Recognition
recognition_map = {
    "Yes, I do feel recognized and acknowledged": "Yes",
    "I somewhat feel recognized and acknowledged": "Somewhat",
    "I don't feel recognized and acknowledged and would prefer staff successes to be highlighted more frequently": "No",
    "I don't feel recognized and acknowledged but I prefer it that way": "No",
    "I do find myself being recognized and acknowledged, but it's rare given the contributions I make": "Somewhat"
}
df['Recognition_Clean'] = df['Do you feel you get acknowledged and recognized for your contribution  at work?'].map(recognition_map).fillna('Unknown')

# Growth
growth_map = {
    "Yes, I do feel there is potential to grow and I hope to advance my career with Homes First": "Yes",
    "There is some potential to grow and I hope to advance my career with Homes First": "Somewhat",
    "There is very little potential to grow although I would like to advance my career with Homes First": "No",
    "Potential to grow seems limited at Homes First and I will likely need to advance my career with another organization": "No",
    "I am not interested in career growth and prefer to remain in my current role": "No"
}
df['Growth_Clean'] = df['Do you feel there is potential for growth at Homes First?'].map(growth_map).fillna('Unknown')

# ----------------------------
# 5. Sidebar Filters
# ----------------------------
st.sidebar.header("Filters")

roles = df['Select the role/department that best describes your current position at Homes First.'].unique()
selected_roles = st.sidebar.multiselect("Select Role/Department", options=roles, default=list(roles))

df_filtered = df[df['Select the role/department that best describes your current position at Homes First.'].isin(selected_roles)]

# ----------------------------
# 6. Summary Metrics
# ----------------------------
st.subheader("Summary Metrics")
col1, col2, col3 = st.columns(3)

col1.metric("Total Respondents", df_filtered.shape[0])
col2.metric("High Fulfillment", df_filtered['Work_Fulfillment_Clean'].value_counts().get('High',0))
col3.metric("Feel Recognized (Yes)", df_filtered['Recognition_Clean'].value_counts().get('Yes',0))

# ----------------------------
# 7. Cross-Analysis Plots
# ----------------------------

st.subheader("Work Fulfillment by Role")
plt.figure(figsize=(12,6))
sns.countplot(data=df_filtered, x='Select the role/department that best describes your current position at Homes First.',
              hue='Work_Fulfillment_Clean', palette='Set2')
plt.xticks(rotation=45, ha='right')
plt.title('Work Fulfillment by Role')
plt.legend(title='Fulfillment')
plt.tight_layout()
st.pyplot(plt.gcf())
plt.clf()

st.subheader("Likelihood to Recommend by Racial/Ethnic Identity")
df_race = df_filtered.explode('Which racial or ethnic identity/identities best reflect you. (Select all that apply.)')
plt.figure(figsize=(12,6))
sns.boxplot(data=df_race, x='Which racial or ethnic identity/identities best reflect you. (Select all that apply.)',
            y='How likely are you to recommend Homes First as a good place to work?', palette='Set3')
plt.xticks(rotation=45, ha='right')
plt.title('Likelihood to Recommend by Racial/Ethnic Identity')
plt.tight_layout()
st.pyplot(plt.gcf())
plt.clf()

st.subheader("Recognition vs Growth (%)")
cross_tab = pd.crosstab(df_filtered['Recognition_Clean'], df_filtered['Growth_Clean'], normalize='index') * 100
plt.figure(figsize=(8,6))
sns.heatmap(cross_tab, annot=True, fmt=".1f", cmap='Blues')
plt.title('Recognition vs Growth')
st.pyplot(plt.gcf())
plt.clf()

st.subheader("Recommendation Score by Work Fulfillment")
plt.figure(figsize=(8,6))
sns.boxplot(data=df_filtered, x='Work_Fulfillment_Clean', y='How likely are you to recommend Homes First as a good place to work?', palette='Pastel1')
plt.title('Recommendation Score by Work Fulfillment')
st.pyplot(plt.gcf())
plt.clf()

# ----------------------------
# 8. Optional: Download Cleaned Data
# ----------------------------
st.subheader("Download Cleaned Dataset")
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(df_filtered)
st.download_button(label="Download CSV", data=csv, file_name='homes_first_survey_cleaned.csv', mime='text/csv')
