# Import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ============================
# 1. Load the dataset
# ============================
import pandas as pd

# Load the Excel file
df = pd.read_excel('Combined- Cross Analysis.xlsx')


# ============================
# 2. Clean multi-select columns
# ============================
# Split multi-select columns into lists
multi_select_cols = [
    'Which racial or ethnic identity/identities best reflect you. (Select all that apply.)',
    'Do you identify as an individual living with a disability/disabilities and if so, what type of disability/disabilities do you have? (Select all that apply.)'
]

for col in multi_select_cols:
    df[col] = df[col].str.split(',').apply(lambda x: [i.strip() for i in x] if isinstance(x, list) else [])

# ============================
# 3. Clean textual categorical responses
# ============================
# Map fulfillment to High / Medium / Low
fulfillment_map = {
    "I find the work I do extremely fulfilling and rewarding": "High",
    "I find the work I do fulfilling and rewarding in some parts and not so much in others": "Medium",
    "I find the work I do somewhat fulfilling and rewarding": "Medium",
    "I don't find the work I do to be fulfilling or rewarding but I like other aspects of the job (such as the hours, the location, the pay/benefits, etc.)": "Low",
    "I don't find the work I do to be fulfilling or rewarding so I am taking steps to change jobs/career path/industry": "Low"
}
df['Work_Fulfillment_Clean'] = df['How fulfilling and rewarding do you find your work?'].map(fulfillment_map)

# Map Recognition to Yes / Somewhat / No
recognition_map = {
    "Yes, I do feel recognized and acknowledged": "Yes",
    "I somewhat feel recognized and acknowledged": "Somewhat",
    "I don't feel recognized and acknowledged and would prefer staff successes to be highlighted more frequently": "No",
    "I don't feel recognized and acknowledged but I prefer it that way": "No",
    "I do find myself being recognized and acknowledged, but it's rare given the contributions I make": "Somewhat"
}
df['Recognition_Clean'] = df['Do you feel you get acknowledged and recognized for your contribution  at work?'].map(recognition_map)

# Map Potential for Growth to Yes / Somewhat / No
growth_map = {
    "Yes, I do feel there is potential to grow and I hope to advance my career with Homes First": "Yes",
    "There is some potential to grow and I hope to advance my career with Homes First": "Somewhat",
    "There is very little potential to grow although I would like to advance my career with Homes First": "No",
    "Potential to grow seems limited at Homes First and I will likely need to advance my career with another organization": "No",
    "I am not interested in career growth and prefer to remain in my current role": "No"
}
df['Growth_Clean'] = df['Do you feel there is potential for growth at Homes First?'].map(growth_map)

# ============================
# 4. Summary statistics
# ============================
# Counts for Role/Department
role_counts = df['Select the role/department that best describes your current position at Homes First.'].value_counts()
print("Role counts:\n", role_counts)

# Counts for racial identity (multi-select exploded)
df_race = df.explode('Which racial or ethnic identity/identities best reflect you. (Select all that apply.)')
race_counts = df_race['Which racial or ethnic identity/identities best reflect you. (Select all that apply.)'].value_counts()
print("Race counts:\n", race_counts)

# Counts for disabilities (multi-select exploded)
df_disability = df.explode('Do you identify as an individual living with a disability/disabilities and if so, what type of disability/disabilities do you have? (Select all that apply.)')
disability_counts = df_disability['Do you identify as an individual living with a disability/disabilities and if so, what type of disability/disabilities do you have? (Select all that apply.)'].value_counts()
print("Disability counts:\n", disability_counts)

# Average Likelihood to Recommend by Role
recommend_avg = df.groupby('Select the role/department that best describes your current position at Homes First.')['How likely are you to recommend Homes First as a good place to work?'].mean()
print("Average recommendation by role:\n", recommend_avg)

# ============================
# 5. Cross-analysis plots
# ============================

# a) Work Fulfillment by Role
plt.figure(figsize=(12,6))
sns.countplot(data=df, x='Select the role/department that best describes your current position at Homes First.',
              hue='Work_Fulfillment_Clean', palette='Set2')
plt.xticks(rotation=45, ha='right')
plt.title('Work Fulfillment by Role')
plt.legend(title='Fulfillment')
plt.tight_layout()
plt.show()

# b) Likelihood to Recommend by Racial Identity
plt.figure(figsize=(12,6))
sns.boxplot(data=df_race, x='Which racial or ethnic identity/identities best reflect you. (Select all that apply.)',
            y='How likely are you to recommend Homes First as a good place to work?', palette='Set3')
plt.xticks(rotation=45, ha='right')
plt.title('Likelihood to Recommend by Racial/Ethnic Identity')
plt.tight_layout()
plt.show()

# c) Recognition vs Growth by Department
cross_tab = pd.crosstab(df['Recognition_Clean'], df['Growth_Clean'], normalize='index') * 100
plt.figure(figsize=(8,6))
sns.heatmap(cross_tab, annot=True, fmt=".1f", cmap='Blues')
plt.title('Recognition vs Growth (%)')
plt.show()

# d) Likelihood to Recommend vs Fulfillment
plt.figure(figsize=(8,6))
sns.boxplot(data=df, x='Work_Fulfillment_Clean', y='How likely are you to recommend Homes First as a good place to work?', palette='Pastel1')
plt.title('Recommendation Score by Work Fulfillment')
plt.show()

# ============================
# 6. Optional: export cleaned dataset
# ============================
df.to_csv('homes_first_survey_cleaned.csv', index=False)
