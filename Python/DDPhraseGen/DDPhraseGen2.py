import argparse
import os
from time import sleep
import pandas as pd
import numpy as np

from OpenAiDDPhraseGen import OpenAiDDPhraseGen

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
    except:
        raise ValueError(f'The file ({filename}) is open and cannot be processed.')


def file_exists(filepath):
    current_working_directory = os.getcwd()
    print(f'Current working directory: {current_working_directory}')
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f'The file {filepath} does not exist.')
    return


def create_table_descriptions_df(filename):
    # Attempt to read the Excel file using Pandas
    try:
        xls = pd.ExcelFile(filename)
    except FileNotFoundError:
        raise Exception(f"The file {filename} does not exist.")
    except Exception as e:
        raise Exception(f"An error occurred while reading the file: {str(e)}")

    # Check for the required sheet names
    required_sheets = ["Table Descriptions", "Tables"]
    sheet_name = None
    for sheet in required_sheets:
        if sheet in xls.sheet_names:
            sheet_name = sheet
            break
    
    # If neither "Table Descriptions" nor "Tables" is found, raise an exception
    if sheet_name is None:
        raise Exception(f"Neither 'Table Descriptions' nor 'Tables' worksheet was found in the Excel file.")

    # Read the data from the found worksheet
    data = pd.read_excel(xls, sheet_name=sheet_name)

    # Create the new DataFrame with the required columns
    table_descriptions = pd.DataFrame(columns=["TableName", "AlreadyInDataHub", "Description"])
    
    # Depending on the worksheet structure, you might need to adjust how you populate the new DataFrame
    # Assuming the worksheet has columns that can be directly mapped to the required columns
    mapping_columns = {
        'TableName': 'TableName',  # Replace 'Table Name' with the actual column name in the sheet
        'AlreadyInDataHub': 'AlreadyInDataHub',  # Replace 'In DataHub' with the actual column name in the sheet
        'Description': 'Description'  # Replace 'Description' with the actual column name in the sheet
    }
    
    # Check if all the required columns are present in the worksheet
    for col in mapping_columns.values():
        if col not in data.columns:
            raise Exception(f"Required column '{col}' is missing in the worksheet '{sheet_name}'.")

    # Map the columns from the worksheet to the new DataFrame
    for col, new_col in mapping_columns.items():
        table_descriptions[new_col] = data[col]

    return table_descriptions


def create_column_descriptions_df(filename):
    """
    Create a DataFrame from an Excel file with specific columns based on a provided sheet.

    Args:
        filename (str): The path to the Excel file.

    Returns:
        pd.DataFrame: A DataFrame with the specified columns.

    Raises:
        ValueError: If the required sheets are not present in the Excel file.
    """
    # Try to load the Excel file
    try:
        xls = pd.ExcelFile(filename)
    except FileNotFoundError:
        raise FileNotFoundError(f'The file {filename} was not found.')
    
    # Check for required sheets
    required_sheets = ['Glossary', 'Column Descriptions']
    sheet_name = None
    for sheet in required_sheets:
        if sheet in xls.sheet_names:
            sheet_name = sheet
            break
    
    if sheet_name is None:
        raise ValueError(f'Excel file must contain a sheet named "Glossary" or "Column Descriptions".')

    # Column mappings for each possible sheet
    column_mappings = {
        'Glossary': {
            'TABLENAME': 'TableName',
            'COLNAME': 'ColumnName',
            'Friendly Name': 'Friendly Name',
            'IncludeInView': 'IncludeInView',
            'Description': 'Description'
        },
        'Column Descriptions': {
            'TableName': 'TableName',
            'ColumnName': 'ColumnName',
            'Friendly Name': 'Friendly Name',
            'IncludeInView': 'IncludeInView',
            'Description': 'Description'
        }
    }

    # Load the data from the correct sheet and select the relevant columns
    df = pd.read_excel(filename, sheet_name=sheet_name)
    selected_columns = column_mappings[sheet_name]
    df = df.rename(columns=selected_columns)
    
    # Ensure only the required columns are in the DataFrame, in the correct order
    df = df[list(selected_columns.values())]

    return df


# def check_worksheets(filename):
#     # Load the Excel file
#     xls = pd.ExcelFile(filename)
    
#     # Check if 'Tables' and 'Glossary' worksheets are present
#     if "Tables" not in xls.sheet_names or "Glossary" not in xls.sheet_names:
#         raise ValueError("The Excel file must have 'Tables' and 'Glossary' worksheets.")
    
#     # Load the 'Tables' worksheet
#     tables_df = xls.parse('Tables')
    
#     # Check if 'TableName' column exists in 'Tables' worksheet
#     if 'TableName' not in tables_df.columns:
#         raise ValueError("The 'Tables' worksheet must have a 'TableName' column.")
    
#     # Check if 'Tables' worksheet has any data rows
#     if tables_df.empty:
#         raise ValueError("The 'Tables' worksheet must have data rows.")
    
#     # Load the 'Glossary' worksheet
#     glossary_df = xls.parse('Glossary')
    
#     # Check if 'TABLENAME' or 'COLNAME' columns exist in 'Glossary' worksheet
#     if 'TABLENAME' not in glossary_df.columns or 'COLNAME' not in glossary_df.columns:
#         raise ValueError("The 'Glossary' worksheet must have 'TABLENAME' and 'COLNAME' columns.")
    
#     # Check if 'Glossary' worksheet has any data rows
#     if glossary_df.empty:
#         raise ValueError("The 'Glossary' worksheet must have data rows.")
    
#     return (tables_df, glossary_df)


# def get_filename_base(filename):
#     # Extract the base file name without the extension
#     fileNameBase = os.path.splitext(os.path.basename(filename))[0]
    
#     # Define the text to search for
#     search_text = "DataDictionary_working"
    
#     # Check if the search_text is in fileNameBase and remove it if present
#     if search_text in fileNameBase:
#         cut_off_index = fileNameBase.find(search_text)
#         fileNameBase = fileNameBase[:cut_off_index]
    
#     return fileNameBase


# def read_data_to_dataframe(filename):
#     df = pd.read_excel(filename, sheet_name="Column Descriptions")
#     return df


# def select_columns(dataframe):
#     # Check if the required columns exist in the dataframe
#     if 'Table Descriptions' not in dataframe.columns or 'Column Descriptions' not in dataframe.columns:
#         raise ValueError("The input dataframe must contain 'Table Descriptions' and 'Column Descriptions' columns.")
    
#     # Select the 'TABLENAME' and 'COLNAME' columns
#     new_dataframe = dataframe[['Table Descriptions', 'Column Descriptions']]
    
#     return new_dataframe


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


def create_unique_filename(desired_filename):

    output_filename = desired_filename
    if os.path.exists(desired_filename):
        fileNameBase = os.path.splitext(os.path.basename(desired_filename))[0]
        fileNameExtension = os.path.splitext(os.path.basename(desired_filename))[1]
        
        # Initialize the counter for the filename
        counter = 0
        # Define the format for the numeric part of the filename
        number_format = "{:03d}"
        # Construct the initial filename
        output_filename = f"{fileNameBase}_{number_format.format(counter)}.{fileNameExtension}"
        
        # Check if the file exists and increment the counter until a unique filename is found
        while os.path.exists(output_filename):
            counter += 1
            output_filename = f"{fileNameBase}_{number_format.format(counter)}.{fileNameExtension}"
       
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


def generateAll(pgen, input_table_descrs, input_column_descrs, output_substring):
    current_column_descrs = input_column_descrs
    continue_looping = True

    try:
        while continue_looping:
            complete, updated_column_descrs = iterateAcrossAiModels(pgen, input_table_descrs, current_column_descrs)
            current_column_descrs = updated_column_descrs
            continue_looping = False
            if not complete:  
                print("Results are not complete after using all AI Models.")         
                user_input = input(f'--Enter "R" if you would like to retry with all AI Models again. Enter "X" to Exit.').strip().lower()
                if user_input == 'r':
                    continue_looping = True
                if user_input == 'q':
                    print('Quitting without writing output file.')
                    exit()
    except Exception as e:
        print(f'!!!Exception: {e}')

    print('Final Results:')
    displayColumnResults(current_column_descrs)
    writeDataFramesToFile(output_substring, input_table_descrs, current_column_descrs)
    return


def iterateAcrossAiModels(pgen, input_table_descrs, input_column_descrs):
    aiModels = pgen.getModelNames()
    print(f'AI Models available: {aiModels}')

    current_column_descrs = input_column_descrs

    for i in reversed(range(len(aiModels))):
        continue_looping = True
        while continue_looping:
            print (f'Using {aiModels[i]}')
            updated_column_descrs = iterateAcrossTables(pgen, i, input_table_descrs, current_column_descrs)
            current_column_descrs = updated_column_descrs
            complete = displayColumnResults(current_column_descrs)
            continue_looping = False
            if not complete: 
                print("  Results are not complete.")          
                user_input = input(f'  --Enter "R" or "N" - "R" to retry with the current AI Model {aiModels[i]}; "N" to go to the next AI Model.').strip().lower()
                if user_input == 'r':
                    continue_looping = True
                if user_input == 'q':
                    print('Quitting without writing output file...')
                    exit()
    return complete, current_column_descrs


def iterateAcrossTables(pgen, aiModelIndex, input_table_descrs, input_column_descrs):
    tables = input_table_descrs['TableName'].tolist()

    current_column_descrs = input_column_descrs

    for table in tables:
        #print (table)
        updated_column_descrs = processTableData(pgen, aiModelIndex, current_column_descrs)
        current_column_descrs = updated_column_descrs
    return updated_column_descrs


def processTableData(pgen, aiModelIndex, column_descrs):
    updated_column_descrs = column_descrs
    return updated_column_descrs


def displayColumnResults(column_descriptions):
    print(f'  Current Column Results:')
    columns = column_descriptions['ColumnName'].tolist()
    friendlyNames = column_descriptions['Friendly Name'].tolist()
    descriptions = column_descriptions['Description'].tolist()
    columnCount = len(columns)
    print(f'  Number of Columns: {columnCount}')
    populatedFriendlyNameCount = countNonEmptyNonNanItems(friendlyNames)
    populatedFriendlynamePercent = 100 * (populatedFriendlyNameCount / columnCount)
    print(f'  Number of filled-in Friendly Names: {populatedFriendlyNameCount} ({populatedFriendlynamePercent} %)')
    populatedDescriptionCount = countNonEmptyNonNanItems(descriptions)
    populatedDescriptionPercent = 100 * (populatedDescriptionCount / columnCount)
    print(f'  Number of filled-in Descriptions: {populatedDescriptionCount} ({populatedDescriptionPercent} %)')
    totalPercentComplete = 100 * (populatedFriendlyNameCount + populatedDescriptionCount) / (2 * columnCount)
    print(f'  Total percent complete: {totalPercentComplete} %')

    if (populatedFriendlyNameCount + populatedDescriptionCount) < (2 * columnCount):
        return False
    else:
        return True


def writeDataFramesToFile(output_substring, table_descrs, column_descrs):
    base_output_filename = f'{output_substring}_Descriptions.xlsx'
    output_filename = create_unique_filename(base_output_filename)

    print(f'Writing output file: {output_filename}')
    create_excel_with_sheets(output_filename, "Table Descriptions", table_descrs, "Column Descriptions", column_descrs)

    return


def create_excel_with_sheets(output_file_name, worksheet_name1, dataframe1, worksheet_name2, dataframe2):
    # Check if the file name ends with '.xlsx'
    if not output_file_name.endswith('.xlsx'):
        raise ValueError("Output file name must end with '.xlsx'")
    
    # Replace NaN values with empty strings in both dataframes
    dataframe1 = dataframe1.replace({np.nan: ''})
    dataframe2 = dataframe2.replace({np.nan: ''})
    
    # Create an Excel writer object
    with pd.ExcelWriter(output_file_name, engine='openpyxl') as writer:
        # Write the first dataframe to the first worksheet
        dataframe1.to_excel(writer, sheet_name=worksheet_name1, index=False)
        
        # Write the second dataframe to the second worksheet
        dataframe2.to_excel(writer, sheet_name=worksheet_name2, index=False)


def countNonEmptyNonNanItems(input_list):
    # Count items that are not NaN and not empty strings
    count = sum(1 for item in input_list if not pd.isna(item) and item != "")
    return count



def main():
    parser = argparse.ArgumentParser(description="Process a Data Dictionary file and generate AI Prompts for Friendly Names and Descriptions.")
    parser.add_argument("-i", "--input", required=True, help="Input Excel file (with .xlsx extension)")
    parser.add_argument("-o", "--output", required=True, help="Output substring to use to create the output file.")
    parser.add_argument("-d", "--dbDescription", required=True, help="A one word description of the database being described.")
    
    args = parser.parse_args()

    input_file = args.input
    db_Description = args.dbDescription
    output_substring = args.output

    # Check if the file has the correct extension
    check_file_extension(input_file)
    
    # Check if the file exists
    file_exists(input_file)

    # Check if the file is open
    check_if_file_open(input_file)
    
    print(input_file)
    table_descriptions = create_table_descriptions_df(input_file)
    #print(table_descriptions)
    column_descriptions = create_column_descriptions_df(input_file)   
    #print(column_descriptions)

    pgen = OpenAiDDPhraseGen()
    generateAll(pgen, table_descriptions, column_descriptions, output_substring)
    print('Done.')


if __name__ == "__main__":
    main()
