import pandas as pd
import json
import re

def create_new_dataframe(input_df):
    # Initialize lists to store the new column values
    sources = []
    groups = []
    folders = []
    time_periods = []
    calculations = []
    abbrevs = []
    descriptions = []
    formulas = []

    # Iterate through the input dataframe rows
    for index, row in input_df.iterrows():
        group_name = row['GroupName']
        measure = row['Measure']
        folder = row['Folder']
        expression = row['Expression']

        # Determine Source
        if 'Cobra' in group_name:
            source = 'Cobra'
        elif 'Financial' in group_name:
            source = 'Financial'
        elif 'P6' in group_name:
            source = 'P6'
        else:
            source = ''

        # Determine Group
        group = group_name.split()[-1] if group_name else ''

        # Determine Time Period
        if 'CFY' in measure:
            time_period = 'CFY'
        elif 'CP ' in measure:
            time_period = 'CP'
        elif 'Lifecycle' in measure or 'Lifecycle' in folder:
            time_period = 'Lifecycle'
        elif 'PP' in measure or 'Prior Period' in folder:
            time_period = 'PP'
        elif 'Date' in measure:
            time_period = 'Date'
        else:
            time_period = ''

        # Determine Calculation and Abbrev
        calculation = re.sub(r'\s*\([^)]*\)', '', measure).strip()
        abbrev_match = re.search(r'\(([^)]*)\)', measure)
        abbrev = abbrev_match.group(1) if abbrev_match else ''

        # Append values to respective lists
        sources.append(source)
        groups.append(group)
        folders.append(folder)
        time_periods.append(time_period)
        calculations.append(calculation)
        abbrevs.append(abbrev)
        descriptions.append('')  # Description is to be blank
        formulas.append(expression)

    # Create a dictionary to hold the new dataframe data
    data = {
        'Source': sources,
        'Group': groups,
        'Folder': folders,
        'Time Period': time_periods,
        'Calculation': calculations,
        'Abbrev': abbrevs,
        'Description': descriptions,
        'Formula': formulas
    }

    # Create the new dataframe
    new_df = pd.DataFrame(data, columns=['Source', 'Group', 'Folder', 'Time Period', 'Calculation', 'Abbrev', 'Description', 'Formula'])

    return new_df


# Read the JSON file
with open('calculation_groups.json', 'r') as file:
    data = json.load(file)

# Initialize an empty list to store the records
records = []

# Iterate through the calculationgrouptables array
for group in data['calculationgrouptables']:
    group_name = group['name']
    if 'measures' in group:
        for measure in group['measures']:
            measure_name = measure['name']
            expression = measure['expression']
            folder = measure.get('displayFolder', '')  # Default to empty string if 'displayFolder' is not present
            records.append({
                'GroupName': group_name,
                'Measure': measure_name,
                'Folder': folder,
                'Expression': expression
            })

# Create a DataFrame
df = pd.DataFrame(records, columns=['GroupName', 'Measure', 'Folder', 'Expression'])

df2 = create_new_dataframe(df)

# Write the DataFrame to an Excel file with a specific worksheet name
with pd.ExcelWriter('Calculations.xlsx', engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Raw Calc Data', index=False)
    df2.to_excel(writer, sheet_name='Calculations', index=False)

print("Data has been successfully written to the 'Raw Calculations' worksheet in Calculations.xlsx")
