import pandas as pd

# Load the Excel dataset
df = pd.read_excel('/mnt/data/Combined- Cross Analysis.xlsx')

# Standardize columns
df.columns = [
    'Role', 'Ethnicity', 'Disability', 'Work_Fulfillment', 
    'Recommendation_Score', 'Recognition', 'Growth_Potential'
]

# Filter to only the 14 target roles
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

df = df[df['Role'].isin(target_roles)]

# Explode multi-select fields
df_eth = df.assign(Ethnicity=df['Ethnicity'].str.split(',')).explode('Ethnicity')
df_eth['Ethnicity'] = df_eth['Ethnicity'].str.strip()

df_dis = df.assign(Disability=df['Disability'].str.split(',')).explode('Disability')
df_dis['Disability'] = df_dis['Disability'].str.strip()

# Map Recognition & Growth responses to shorter labels
recog_map = {
    'Yes, I do feel recognized and acknowledged': 'Yes',
    'I somewhat feel recognized and acknowledged': 'Somewhat',
    "I do find myself being recognized and acknowledged, but it's rare given the contributions I make": 'Rare',
    "I don't feel recognized and acknowledged and would prefer staff successes to be highlighted more frequently": 'No (Want More)',
    "I don't feel recognized and acknowledged but I prefer it that way": 'No (Prefer)'
}

growth_map = {
    'Yes, I do feel there is potential to grow and I hope to advance my career with Homes First': 'Yes',
    'There is some potential to grow and I hope to advance my career with Homes First': 'Some',
    'Potential to grow seems limited at Homes First and I will likely need to advance my career with another organization': 'Limited',
    'There is very little potential to grow although I would like to advance my career with Homes First': 'Very Limited',
    'I am not interested in career growth and prefer to remain in my current role': 'Not Interested'
}

df['Recognition_Short'] = df['Recognition'].map(recog_map)
df['Growth_Short'] = df['Growth_Potential'].map(growth_map)

# Compute percentages for Recognition and Growth by Role
recog_cross_role = pd.crosstab(
    df['Role'],
    df['Recognition_Short'],
    normalize='index'
) * 100

growth_cross_role = pd.crosstab(
    df['Role'],
    df['Growth_Short'],
    normalize='index'
) * 100
