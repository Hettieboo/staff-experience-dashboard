import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set page
st.set_page_config(page_title="Homes First Survey Dashboard", layout="wide")
st.title("Homes First Staff Experience Dashboard")

# Load dataset
df = pd.read_excel('Combined- Cross Analysis.xlsx')

# Multi-select clean
multi_select_cols = [
    'Which racial or ethnic identity/identities best reflect you. (Select all that apply.)',
    'Do you identify as an individual living with a disability/disabilities and if so, what type of disability/disabilities do you have? (Select all that apply.)'
]
for col in multi_select_cols:
    df[col] = df[col].astype(str).str.split(r',|;').apply(lambda x: [i.strip() for i in x] if isinstance(x, list) else [])

# Clean categorical responses (example for Fulfillment)
fulfillment_map = {
    "I find the work I do extremely fulfilling and rewarding": "High",
    "I find the work I do fulfilling and rewarding in some parts and not so much in others": "Medium",
    "I find the work I do somewhat fulfilling and rewarding": "Medium",
    "I don't find the work I do to be fulfilling or rewarding but I like other aspects of the job (such as the hours, the location, the pay/benefits, etc.)": "Low",
    "I don't find the work I do to be fulfilling or rewarding so I am taking steps to change jobs/career path/industry": "Low"
}
df['Work_Fulfillment_Clean'] = df['How fulfilling and rewarding do you find your work?'].map(fulfillment_map).fillna('Unknown')

# Sidebar filters
roles = df['Select the role/department that best describes your current position at Homes First.'].unique()
selected_roles = st.sidebar.multiselect("Select Role/Department", roles, default=list(roles))
df_filtered = df[df['Select the role/department that best describes your current position at Homes First.'].isin(selected_roles)]

# Select question and chart type
question_cols = ['Work_Fulfillment_Clean', 'Recognition_Clean', 'Growth_Clean']
chart_types = ['Horizontal Bar', 'Vertical Bar', 'Pie', 'Donut', 'Scatter']

selected_question = st.selectbox("Select Question", question_cols)
selected_chart = st.selectbox("Select Chart Type", chart_types)

# Explode if multi-select
if selected_question in multi_select_cols:
    df_plot = df_filtered.explode(selected_question)
else:
    df_plot = df_filtered.copy()

# Plotting
st.subheader(f"{selected_chart} of {selected_question}")

if selected_chart == 'Horizontal Bar':
    counts = df_plot[selected_question].value_counts()
    counts.plot(kind='barh', figsize=(10, max(6, len(counts)/2)), color=sns.color_palette('Set2'))
    plt.xlabel("Count")
    plt.ylabel(selected_question)
    st.pyplot(plt.gcf())
    plt.clf()

elif selected_chart == 'Vertical Bar':
    counts = df_plot[selected_question].value_counts()
    counts.plot(kind='bar', figsize=(10,6), color=sns.color_palette('Set3'))
    plt.ylabel("Count")
    plt.xlabel(selected_question)
    plt.xticks(rotation=45, ha='right')
    st.pyplot(plt.gcf())
    plt.clf()

elif selected_chart == 'Pie':
    counts = df_plot[selected_question].value_counts()
    counts.plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
    plt.ylabel("")
    st.pyplot(plt.gcf())
    plt.clf()

elif selected_chart == 'Donut':
    counts = df_plot[selected_question].value_counts()
    wedges, texts, autotexts = plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
    plt.gca().add_artist(plt.Circle((0,0),0.5,fc='white'))
    st.pyplot(plt.gcf())
    plt.clf()

elif selected_chart == 'Scatter':
    numeric_col = 'How likely are you to recommend Homes First as a good place to work?'
    sns.scatterplot(data=df_plot, x=numeric_col, y=selected_question, hue='Select the role/department that best describes your current position at Homes First.', palette='Set2', alpha=0.7)
    plt.xticks(rotation=45)
    st.pyplot(plt.gcf())
    plt.clf()
