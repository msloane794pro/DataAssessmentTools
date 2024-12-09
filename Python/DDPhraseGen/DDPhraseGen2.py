import argparse
import os
from time import sleep
import pandas as pd
import numpy as np
from datetime import datetime
import csv
from io import StringIO

from OpenAiDDPhraseGen import OpenAiDDPhraseGen
from OpenAiDDPhraseGen import PhraseType as pt

tableNameSubstPattern = '~~~tableName~~~'
dbDescrSubstPattern = '~~~dbDescrSubst~~~'

backup_current_column_descrs = pd.DataFrame()

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


# def dataframe_to_dict(df):
#     return df.to_dict('list')


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
        output_filename = f"{fileNameBase}_{number_format.format(counter)}{fileNameExtension}"
        
        # Check if the file exists and increment the counter until a unique filename is found
        while os.path.exists(output_filename):
            counter += 1
            output_filename = f"{fileNameBase}_{number_format.format(counter)}{fileNameExtension}"
       
    return output_filename


def generateAll(pgen, db_Description, input_table_descrs, input_column_descrs, output_substring, reverse):
    global backup_current_column_descrs
    
    print('Input Status:')
    displayColumnResults(input_column_descrs)
    backup_current_column_descrs = input_column_descrs.copy()
    current_column_descrs = input_column_descrs
    continue_looping = True

    try:
        while continue_looping:
            complete, updated_column_descrs = iterateAcrossAiModels(pgen, db_Description, input_table_descrs, current_column_descrs, reverse)
            current_column_descrs = updated_column_descrs.copy()
            continue_looping = False
            if not complete:  
                print("Results are not complete after using all AI Models.")         
                user_input = input(f'----Enter "R" | "S" | "Q" - "R" to retry with all AI Models again. "S" to Save and exit. "Q" to quit immediately.').strip().lower()
                if user_input == 'r':
                    continue_looping = True
                if user_input == 'q':
                    print('Quitting without writing output file.')
                    exit()
    except Exception as e:
        print(f'!!!Exception: {e}')
        current_column_descrs = backup_current_column_descrs
        print('Using back-up column descriptions object.')

    print('Final Results:')
    displayColumnResults(current_column_descrs)
    writeDataFramesToFile(output_substring, input_table_descrs, current_column_descrs)
    return


def iterateAcrossAiModels(pgen, dbDescr, input_table_descrs, input_column_descrs, reverse):
    aiModelsRaw = pgen.getModelNames()
    print(f'Raw AI Models available: {aiModelsRaw}')
    print (f'reverseOrder param = {reverse}')

    if reverse:
        aiModels = list(reversed(aiModelsRaw))
        print('Reversed')
    else:
        aiModels = aiModelsRaw
        print('Not Reversed')

    print(f'AI Models available: {aiModels}')
    numAiModels = len(aiModels)
    print(f'Number of AI Models available: {numAiModels}')

    current_column_descrs = input_column_descrs.copy()

    for i in reversed(range(len(aiModels))):
        continue_looping = True
        while continue_looping:
            print (f'Using {aiModels[i]}')
            updated_column_descrs = iterateAcrossTables(pgen, i, dbDescr, input_table_descrs, current_column_descrs)
            current_column_descrs = updated_column_descrs.copy()
            print(f'Results after Table Cycle using {aiModels[i]}:')
            complete = displayColumnResults(current_column_descrs)
            continue_looping = False
            if not complete: 
                print("  Results are not complete.")          
                user_input = input(f'  --Enter "R" | "N" | "Q" - "R" to retry AI Model {aiModels[i]}; "N" to go to the next AI Model; "Q" to quit.').strip().lower()
                if user_input == 'r':
                    continue_looping = True
                if user_input == 'q':
                    print('Quitting without writing output file...')
                    exit()

    return complete, current_column_descrs


def iterateAcrossTables(pgen, aiModelIndex, dbDescr, input_table_descrs, input_column_descrs):
    tables = input_table_descrs['TableName'].tolist()

    current_column_descrs = input_column_descrs

    numTables = len(tables)
    tableNum = 1

    for table in tables:
        print (f'({tableNum} of {numTables}) Generating phrases for table: {table}...')
        tableNum += 1
        updated_column_descrs = processTableData(pgen, aiModelIndex, dbDescr, table, current_column_descrs)
        current_column_descrs = updated_column_descrs.copy()
        
    return current_column_descrs


def processTableData(pgen, aiModelIndex, dbDescr, table_name, column_descrs):
    global backup_current_column_descrs
    updated_column_descrs = column_descrs.copy()
    pgen.setModel(aiModelIndex)

    filtered_df = column_descrs[column_descrs['TableName'] == table_name]
    elementList = filtered_df['ColumnName'].tolist()
    numElements = len(elementList)

    if (check_for_empty_column_values(filtered_df, "Friendly Name")):
        print(f'...Friendly Name...({numElements} elements)')
        sessionType = pt.FRIENDLYNAME
        current_time = datetime.now()
        sessionId = f'{table_name}_fnames_{current_time.strftime("%Y%m%d%H%M%S")}'
        responseText = pgen.sendSinglePrompt(sessionId, sessionType, dbDescr, table_name, elementList)
        responseList = splitAndFilterLines(responseText)
        if len(responseList) != len(elementList):
            print(f'   ~~~Incorrect number of lines in Friendly name response.  {len(elementList)} expected, {len(responseList)} received.')
        else:
            try:
                fnameDf = create_fname_dataframe(responseList)
                updated_column_descrs = update_friendly_names(updated_column_descrs, fnameDf)
            except:
                print(f'   ~~~Incorrect formatting in Friendly name response.  {len(responseList)} received, but not in proper CSV format.')

        csvFileName = f'.\\respcsv\\{sessionId}.csv'
        write_stringList_to_file(csvFileName, responseList)
        backup_current_column_descrs = updated_column_descrs.copy()
        sleep(1)
    else:
        print(f'   Friendly Names already filled in!  Yay!')

    if (check_for_empty_column_values(filtered_df, "Description")):
        print(f'...Description...({numElements} elements)')
        sessionType = pt.DESCRIPTION
        current_time = datetime.now()
        sessionId = f'{table_name}_descrs_{current_time.strftime("%Y%m%d%H%M%S")}'
        responseText = pgen.sendSinglePrompt(sessionId, sessionType, dbDescr, table_name, elementList)
        responseList = splitAndFilterLines(responseText)
        if len(responseList) != len(elementList):
            print(f'   ~~~Incorrect number of lines in Description response.  {len(elementList)} expected, {len(responseList)} received.')
        else:
            try:
                descrDf = create_descr_dataframe(responseList)
                updated_column_descrs = update_descriptions(updated_column_descrs, descrDf)
            except:
                print(f'   ~~~Incorrect formatting in Description response.  {len(responseList)} received, but not in proper CSV format.')

        csvFileName = f'.\\respcsv\\{sessionId}.csv'
        write_stringList_to_file(csvFileName, responseList)
        backup_current_column_descrs = updated_column_descrs.copy()
        sleep(1)
    else:
        print(f'   Descriptions already filled in!  Yay!')      

    return updated_column_descrs


def update_friendly_names(column_descrs, fnameDf):
    # Perform a left join on the 'TableName' and 'ColumnName' columns
    merged_df = column_descrs.merge(fnameDf[['TableName', 'ColumnName', 'Friendly Name']], 
                                    on=['TableName', 'ColumnName'], 
                                    how='left', 
                                    suffixes=('', '_fnameDf'))

    # Update the 'Friendly Name' column in column_descrs with the values from fnameDf
    merged_df['Friendly Name'] = merged_df['Friendly Name_fnameDf'].combine_first(merged_df['Friendly Name'])

    # Drop the merged 'Friendly Name_fnameDf' column as it's no longer needed
    merged_df.drop(columns=['Friendly Name_fnameDf'], inplace=True)
    
    return merged_df


def update_descriptions(column_descrs, descrDf):
    # Perform a left join on the 'TableName' and 'ColumnName' columns
    merged_df = column_descrs.merge(descrDf[['TableName', 'ColumnName', 'Description']], 
                                    on=['TableName', 'ColumnName'], 
                                    how='left', 
                                    suffixes=('', '_descrDf'))

    # Update the 'Description' column in column_descrs with the values from descrDf
    merged_df['Description'] = merged_df['Description_descrDf'].combine_first(merged_df['Description'])

    # Drop the merged 'Description_descrDf' column as it's no longer needed
    merged_df.drop(columns=['Description_descrDf'], inplace=True)
    
    return merged_df


def check_for_empty_column_values(df: pd.DataFrame, column_name: str) -> bool:
    # Check if the column exists in the DataFrame
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")
    
    # Check if all values in the column are NaN or empty
    all_nan_or_empty = df[column_name].isna() | (df[column_name].astype(str).str.strip() == '')
    
    # Return True if all values are NaN or empty, otherwise return False
    return all_nan_or_empty.all()


def create_fname_dataframe(input_list):
    # Define a helper function to clean the 'Friendly Name' field
    def clean_friendly_name(friendly_name):
        # Strip leading and trailing double-quote and single-quote characters
        friendly_name = friendly_name.strip('"').strip("'")
        # Replace underscore characters
        friendly_name = friendly_name.replace('_', '')
        return friendly_name

    # Initialize lists to store the data for each column
    table_names = []
    column_names = []
    friendly_names = []

    # Process each string in the input list
    for item in input_list:
        # Check if the item has exactly two commas
        if item.count(',') == 2:
            table_name, column_name, friendly_name = item.split(',')
            table_names.append(table_name)
            column_names.append(column_name)
            cleaned_friendly_name = clean_friendly_name(friendly_name)
            friendly_names.append(cleaned_friendly_name)
        else:
            raise ValueError("Friendly Name Input list not formatted correctly: {item}")

    # Create a DataFrame from the lists
    df = pd.DataFrame({
        'TableName': table_names,
        'ColumnName': column_names,
        'Friendly Name': friendly_names
    })

    return df


def create_descr_dataframe(input_list):
    # Define a helper function to clean the 'Friendly Name' field
    def clean_descriptions(description):
        # Strip leading and trailing double-quote and single-quote characters
        description = description.strip('"').strip("'")
        # Replace underscore characters
        description = description.replace('_', '')
        return description

    # Initialize lists to store the data for each column
    table_names = []
    column_names = []
    descriptions = []

    # Process each string in the input list
    for item in input_list:
        # Use csv.reader to correctly split the string while respecting quotes
        f = StringIO(item)
        reader = csv.reader(f, delimiter=',', quotechar='"', skipinitialspace=True)
        parsed_item = next(reader)
        
        # Check if the parsed item has exactly three elements
        if len(parsed_item) == 3:
            table_name, column_name, description = parsed_item
            table_names.append(table_name)
            column_names.append(column_name)
            cleaned_description = clean_descriptions(description)
            descriptions.append(cleaned_description)
        else:
            raise ValueError(f"Description Input list not formatted correctly: {item}")

    # Create a DataFrame from the lists
    df = pd.DataFrame({
        'TableName': table_names,
        'ColumnName': column_names,
        'Description': descriptions
    })

    return df


def splitAndFilterLines(multiLineString):
    # List of unwanted substrings
    unwanted_substrings = [
        "Here is a list of friendly names",
        "Here is the list of friendly names",
        "here is the list of friendly names",
        "Here's the list of friendly names",
        "here's the list of friendly names",
        "Here are the friendly names",
        "Here are the list of friendly names",
        "here are the list of friendly names",
        "here are their respective friendly names",
        "friendly names are as follows",
        "Below is the list of friendly names",
        "below is the list of friendly names",
        "The list of friendly names for each data element name is",
        "The friendly names for the data element names are as follows",
        "Here is the output with friendly names",
        "Here is a description for each data element",
        "Here is the description for each data element",
        "Please find the descriptions below",
        "Here is the list of descriptions for each data element",
        "This list is derived from the",
        "The response would be as follows",
        "The list of friendly names for the",
        "Here's a description for each data element",
        "To provide descriptions for each data element based on the column names",
        "Here is the list of descriptions for each column",
        "Below is a description for each data element",
        "Here is the list of descriptions",
        "Below is a list of friendly names",
        "Here is the description of each data element",
        "Here is the list of column names with their respective friendly names",
        "each individual Friendly Name on a separate line of text",
        "Here is a multi-line list of the column names",
        "The format you provided is not a standard data interchange format",
        "Here is a potential description for each data element",
        "Here is the friendly name for each column name",
        "Here's the list of descriptions for each data element",
        "The following is a list of friendly names",
        "The given task is a request to create a friendly name for each column name",
        "These friendly names are created by interpreting",
        "Please note that the friendly names are generated",
        "Here's the description for each data element",
        "for a friendly name to be created",
        "THE FRIENDLY NAMES WOULD BE",
        "here are the descriptions for each data element",
        "Please note that the provided instructions",
        "'''",
        "```"
    ]
    
    # Convert unwanted substrings to lowercase
    unwanted_substrings_lower = [unwanted.lower() for unwanted in unwanted_substrings]
    
    # Split the multi-line string into a list and filter out blank lines and lines containing any unwanted substrings (case-insensitive)
    lines_list = [
        line for line in multiLineString.splitlines()
        if line.strip() and not any(unwanted in line.lower() for unwanted in unwanted_substrings_lower)
    ]
    
    return lines_list


def write_stringList_to_file(file_path, stringList):
    directory_name = "respcsv"

    # Check if the directory exists
    if not os.path.exists(directory_name):
        # If it does not exist, create the directory
        os.makedirs(directory_name)
        
    with open(file_path, 'w') as file:
        for stringItem in stringList:
            file.write(stringItem + '\n')


def displayColumnResults(column_descriptions):
    #print(f'  Current Column Results:')
    columns = column_descriptions['ColumnName'].tolist()
    friendlyNames = column_descriptions['Friendly Name'].tolist()
    descriptions = column_descriptions['Description'].tolist()
    columnCount = len(columns)
    print(f'  Number of Columns: {columnCount}')
    populatedFriendlyNameCount = countNonEmptyNonNanItems(friendlyNames)
    populatedFriendlynamePercent = 100 * (populatedFriendlyNameCount / columnCount)
    print(f'  Number of filled-in Friendly Names: {populatedFriendlyNameCount} ({populatedFriendlynamePercent:.1f} %)')
    populatedDescriptionCount = countNonEmptyNonNanItems(descriptions)
    populatedDescriptionPercent = 100 * (populatedDescriptionCount / columnCount)
    print(f'  Number of filled-in Descriptions: {populatedDescriptionCount} ({populatedDescriptionPercent:.1f} %)')
    totalPercentComplete = 100 * (populatedFriendlyNameCount + populatedDescriptionCount) / (2 * columnCount)
    print(f'  Total percent complete: {totalPercentComplete:.1f} %')

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
    parser.add_argument("-r", "--reverseOrder", required=False, help="Reverse order of AI model iteration.  True | False")
    
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

    # Check if reverseOrder is provided and validate its value
    if args.reverseOrder is not None:
        if args.reverseOrder.lower() in ['true', 'false']:
            reverse = args.reverseOrder.lower() == 'true'
        else:
            raise ValueError("Invalid value for --reverseOrder. Please provide either True or False.")
    else:
        reverse = False

    pgen = OpenAiDDPhraseGen()
    generateAll(pgen, db_Description, table_descriptions, column_descriptions, output_substring, reverse)
    print('Done.')


if __name__ == "__main__":
    main()
