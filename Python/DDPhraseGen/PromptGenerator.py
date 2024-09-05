import argparse
import os
from time import sleep
import pandas as pd

tableNameSubstPattern = '~~~tableName~~~'
dbDescrSubstPattern = '~~~dbDescrSubst~~~'

_frientlyNamePrompt = f"""I will provide you with a list of column names from a `{dbDescrSubstPattern}` database table named `{tableNameSubstPattern}`. 
For each column name, I need you to create a `Friendly Name` as follows:
The friendly name for each column name is to be a human readable set of one or more words, derived from the column name.
Each friendly name returned should have the first letter of each word in upper case and all other characters in lower case.
Search through the text of each element name and break it up into one or more words seperated by spaces.
Any substring within the element name that matches an English word should be considered one of the seperated words.
If an element name contains a substring that matches a well known English abbreivation, the full text of the abbreviated item should be considered one of the seperated words.
For example the element name HORSEDR should result in the following: Horse Doctor
Interpret the use of camel case or Pascal case within the element name as defining a word boundary.
For example the element name AssessingMissionCenterName would be separated into the following words: Assessing Mission Center Name
Interpret the `_` character within a column name as defining a word boundary.
For example ApprRequestForm_ID would be separated into the following words: Appr Request Form ID
Another example is Escort_ID would be separated into the following words: Escort ID
Another example is LOGEndDate would be separated into the following words: Log End Date
If the column name consists of a single word, return that word only.
For example a column name of "BUILDING" would result in the following: Building
Do not include the underscore character `_` in your response.
Do not include an escaped underscore character such as `\_` in your response.
In your response, return exactly one line of words for each column name.
For example, if the list of column names provided has 12 columns listed, your response must contain exactly 12 lines of text.
Return the results as a multi-line list, with each individual Friendly Name on a separate line of text.
For each line in your response, format the line as follows: <table name>,<column name>,<friendly name>
Insert a "~" in between each line of text.
Here is the list of column names:
"""

_descriptionPrompt = f"""I will provide you with a list of column names from a `{dbDescrSubstPattern}` database table named `{tableNameSubstPattern}`. 
Produce a description for each data element. 
Wrap each description in double quotes.
Return the results as a multi-line list, with each individual Description on a separate line of text.
For each line in your response, format the line as follows: <table name>,<column name>,<description>
Insert a "~" in between each line of text.
Here is the list of column names:
"""

def check_file_extension(filename):
    if not filename.endswith(".xlsx"):
        raise ValueError("Input file must have a '.xlsx' extension.")


def check_if_file_open(filename):
    try:
        os.rename(filename, filename)
    except OSError:
        raise ValueError("The file is open and cannot be processed.")


def check_worksheets(filename):
    # Load the Excel file
    xls = pd.ExcelFile(filename)
    
    # Check if 'Tables' and 'Glossary' worksheets are present
    if "Tables" not in xls.sheet_names or "Glossary" not in xls.sheet_names:
        raise ValueError("The Excel file must have 'Tables' and 'Glossary' worksheets.")
    
    # Load the 'Tables' worksheet
    tables_df = xls.parse('Tables')
    
    # Check if 'TableName' column exists in 'Tables' worksheet
    if 'TableName' not in tables_df.columns:
        raise ValueError("The 'Tables' worksheet must have a 'TableName' column.")
    
    # Check if 'Tables' worksheet has any data rows
    if tables_df.empty:
        raise ValueError("The 'Tables' worksheet must have data rows.")
    
    # Load the 'Glossary' worksheet
    glossary_df = xls.parse('Glossary')
    
    # Check if 'TABLENAME' or 'COLNAME' columns exist in 'Glossary' worksheet
    if 'TABLENAME' not in glossary_df.columns or 'COLNAME' not in glossary_df.columns:
        raise ValueError("The 'Glossary' worksheet must have 'TABLENAME' and 'COLNAME' columns.")
    
    # Check if 'Glossary' worksheet has any data rows
    if glossary_df.empty:
        raise ValueError("The 'Glossary' worksheet must have data rows.")
    
    return (tables_df, glossary_df)


def get_filename_base(filename):
    # Extract the base file name without the extension
    fileNameBase = os.path.splitext(os.path.basename(filename))[0]
    
    # Define the text to search for
    search_text = "DataDictionary_working"
    
    # Check if the search_text is in fileNameBase and remove it if present
    if search_text in fileNameBase:
        cut_off_index = fileNameBase.find(search_text)
        fileNameBase = fileNameBase[:cut_off_index]
    
    return fileNameBase


def read_data_to_dataframe(filename):
    df = pd.read_excel(filename, sheet_name="Column Descriptions")
    return df


def select_columns(dataframe):
    # Check if the required columns exist in the dataframe
    if 'Table Descriptions' not in dataframe.columns or 'Column Descriptions' not in dataframe.columns:
        raise ValueError("The input dataframe must contain 'Table Descriptions' and 'Column Descriptions' columns.")
    
    # Select the 'TABLENAME' and 'COLNAME' columns
    new_dataframe = dataframe[['Table Descriptions', 'Column Descriptions']]
    
    return new_dataframe


def dataframe_to_dict(df):
    return df.to_dict('list')


def write_data_to_unique_file(data_string, output_filename_base):
    # Initialize the counter for the filename
    counter = 0
    # Define the format for the numeric part of the filename
    number_format = "{:03d}"
    # Construct the initial filename
    output_filename = f"{output_filename_base}_{number_format.format(counter)}.txt"
    
    # Check if the file exists and increment the counter until a unique filename is found
    while os.path.exists(output_filename):
        counter += 1
        output_filename = f"{output_filename_base}_{number_format.format(counter)}.txt"
    
    # Write the data string to the output file
    with open(output_filename, 'w') as file:
        file.write(data_string)
    
    return output_filename


def getTableList(df):
    # Check if 'TableName' column exists
    if 'TableName' not in df.columns:
        raise ValueError("DataFrame must have a 'TableName' column.")
    
    # Get the list of table names from the 'TableName' column
    table_list = df['TableName'].dropna().astype(str).tolist()
    
    return table_list


def getColumnNameList(df, tableName):
    # Check if 'TABLENAME' and 'COLNAME' columns exist
    if 'TABLENAME' not in df.columns or 'COLNAME' not in df.columns:
        raise ValueError("DataFrame must have 'TABLENAME' and 'COLNAME' columns.")

    # Filter the DataFrame for rows where 'TABLENAME' matches the tableName parameter
    filtered_df = df[df['TABLENAME'] == tableName]

    # Get the list of column names from the 'COLNAME' column
    column_name_list = filtered_df['COLNAME'].dropna().astype(str).tolist()

    return column_name_list


def generateFriendlyNamePrompts(tables_df, glossary_df, fileNameBase, dbDescription):
    tableList = getTableList(tables_df)

    # Iterate through each table name in the table list
    for tableName in tableList:
        genFileName = fileNameBase + tableName +'_fName_Prompt'
        # Call getColumnNameList for each table name and pass in the glossary_df
        column_name_list = getColumnNameList(glossary_df, tableName)       
        prompt = _frientlyNamePrompt.replace(dbDescrSubstPattern, dbDescription).replace(tableNameSubstPattern, tableName)
        promptText = prompt + '\n'.join(column_name_list) + '\n'
        fileName = write_data_to_unique_file(promptText, genFileName)
        print(f'{fileName} generated.')

    return 
    


def generateDescriptionPrompts(tables_df, glossary_df, fileNameBase, dbDescription):
    tableList = getTableList(tables_df)

    # Iterate through each table name in the table list
    for tableName in tableList:
        genFileName = fileNameBase + tableName +'_Description_Prompt'
        # Call getColumnNameList for each table name and pass in the glossary_df
        column_name_list = getColumnNameList(glossary_df, tableName)       
        prompt = _descriptionPrompt.replace(dbDescrSubstPattern, dbDescription).replace(tableNameSubstPattern, tableName)
        promptText = prompt + '\n'.join(column_name_list) + '\n'
        fileName = write_data_to_unique_file(promptText, genFileName)
        print(f'{fileName} generated.')
    return



def generateTemplateDescriptionsFile(tables_df, glossary_df, fileNameBase):
    # Create 'table_descriptions' DataFrame
    table_descriptions = tables_df[['TableName']].copy()
    table_descriptions['AlreadyInDataHub'] = 'N'
    table_descriptions['Description'] = ''
    
    # Create 'column_descriptions' DataFrame
    column_descriptions = glossary_df[['TABLENAME', 'COLNAME', 'Friendly Name', 'Description']].copy()
    column_descriptions['IncludeInView'] = 'Y'
    column_descriptions.rename(columns={'TABLENAME': 'TableName', 'COLNAME': 'ColumnName'}, inplace=True)
    column_descriptions = column_descriptions[['TableName', 'ColumnName', 'Friendly Name', 'IncludeInView', 'Description']]
    
    # Define the base output filename
    output_filename = f"{fileNameBase}_Descriptions.xlsx"
    
    # Check if file already exists and modify the filename accordingly
    nnn = 0
    while os.path.isfile(output_filename):
        output_filename = f"{fileNameBase}_Descriptions_{nnn:03d}.xlsx"
        nnn += 1
    
    # Create a Pandas Excel writer using XlsxWriter as the engine
    with pd.ExcelWriter(output_filename, engine='xlsxwriter') as writer:
        # Step 3: Write 'table_descriptions' DataFrame to a worksheet named "Table Descriptions"
        table_descriptions.to_excel(writer, sheet_name='Table Descriptions', index=False)
        
        # Step 4: Write 'column_descriptions' DataFrame to a worksheet named "Column Descriptions"
        column_descriptions.to_excel(writer, sheet_name='Column Descriptions', index=False)
    
    # Return the final output filename
    return output_filename



def generatePrompts(tables_df, glossary_df, fileNameBase, db_Description):
    generateFriendlyNamePrompts(tables_df, glossary_df, fileNameBase, db_Description)
    sleep(2)
    generateDescriptionPrompts(tables_df, glossary_df, fileNameBase, db_Description)
    descriptionsFileName = generateTemplateDescriptionsFile(tables_df, glossary_df, fileNameBase)
    print(f'Empty Descriptions file created: {descriptionsFileName}')
    return


def main():
    parser = argparse.ArgumentParser(description="Process a Data Dictionary file and generate AI Prompts for Friendly Names and Descriptions.")
    parser.add_argument("-i", "--input", required=True, help="Input Excel file (with .xlsx extension)")
    parser.add_argument("-d", "--dbDescription", required=True, help="A one word description of the database being described.")
    
    args = parser.parse_args()

    input_file = args.input
    db_Description = args.dbDescription

    # Check if the file has the correct extension
    check_file_extension(input_file)
    
    # Check if the file is open
    check_if_file_open(input_file)
    
    # Check if the file has the required worksheets, and if the worksheets are correct.
    tables, glossary = check_worksheets(input_file)
    
    fileNameBase = get_filename_base(input_file)

    generatePrompts(tables, glossary, fileNameBase, db_Description)


if __name__ == "__main__":
    main()
