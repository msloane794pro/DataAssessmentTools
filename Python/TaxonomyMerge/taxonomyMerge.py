import argparse
import os
import sys
import pandas as pd
import os
import shutil
from datetime import datetime
import time
import glob


# Constants
TAXONOMY_FILE = "CentralTaxonomyFile.xlsx"
TAXONOMY_GLOSSARY = "Taxonomy Glossary"
ARCHIVE_DIR = "Archive"


def runInitialMerge(initialMergeFile):
    if os.path.isfile(TAXONOMY_FILE):
        print(f'Taxonomy file ({TAXONOMY_FILE}) already exists.  Unable to perform initial merge.')
        return
    else:
        print(f'Running initial merge using {initialMergeFile}')
        if validate_initialMerge_files(initialMergeFile):
            print(f'All data files listed {initialMergeFile} in are present. Ready to process the initial merge.')
            process_initialMerge_file(initialMergeFile)
        else:
            print(f'ERROR: Data files listed {initialMergeFile} are missing.')



def runMerge(domainVal, appVal, moduleVal, ddFile, glossaryTab):
    print(f'Running merge:  {domainVal} - {appVal} - {moduleVal}, Data Dictionary file: {ddFile}, Glossary Tab: {glossaryTab}')

    create_backup_file(TAXONOMY_FILE)

    taxonomy_df = create_taxonomy_df(TAXONOMY_FILE, TAXONOMY_GLOSSARY)

    glossary_df = pd.read_excel(ddFile, sheet_name=glossaryTab)
    glossary_df.insert(0, 'Module', moduleVal)
    glossary_df.insert(0, 'Application', appVal)
    glossary_df.insert(0, 'Domain', domainVal)
    
    cleanUpGlossary(glossary_df)

    updatedTaxonomy_df = append_dataframes(glossary_df, taxonomy_df)
    

    writeFormattedExcelFile(updatedTaxonomy_df, TAXONOMY_FILE, TAXONOMY_GLOSSARY)
    save_file_with_timestamp(TAXONOMY_FILE, ARCHIVE_DIR)
    print(f'...{TAXONOMY_FILE} saved. {len(glossary_df)} rows added')


def append_dataframes(newDataDf, mainDf):
    # Concatenate newDataDf to mainDf and return the resulting dataframe
    if len(mainDf) > 0:
        resultDf = pd.concat([mainDf, newDataDf], ignore_index=True)
        return resultDf
    else:
        return newDataDf


def validate_glossary_columns(df):
    required_columns = ["Domain", "Application", "Module",
            "TABLENAME", "COLNAME", "TYPE", "LEN", "Min Value", "Max Value", "Cardinality", "Max Length", 
            "IsPrimaryKey", "PK_name", "PK_ordinal_position", 
            "IsForeignKey", "FK_name", "FK_referenced_table", "FK_referenced_column", 
            "Friendly Name", "Description", "Notes"
        ]
    # Check if the DataFrame contains all required columns
    return set(required_columns).issubset(set(df.columns))


def create_taxonomy_df(fileName, tabName):
    # Check if the file exists
    if os.path.isfile(fileName):
        try:
            # If the file exists, read the specified sheet into a Pandas dataframe
            df = pd.read_excel(fileName, sheet_name=tabName, index_col=None)
            #print(f"...Dataframe created from {tabName} tab in {fileName}")
        except ValueError as e:
            # Sheet not found in the workbook
            print(f"Tab {tabName} does not exist in {fileName}: {e}")
            #df = pd.DataFrame()  # Return an empty dataframe
        except Exception as e:
            # Handle other exceptions such as file not being an Excel file
            print(f"An error occurred: {e}")
            #df = pd.DataFrame()  # Return an empty dataframe
    else:
        # If the file does not exist, create an empty dataframe with specified columns
        columns = ["Domain", "Application", "Module",
            "TABLENAME", "COLNAME", "TYPE", "LEN", "Min Value", "Max Value", "Cardinality", "Max Length", 
            "IncludeInView", "IsPrimaryKey", "PK_name", "PK_ordinal_position", 
            "IsForeignKey", "FK_name", "FK_referenced_table", "FK_referenced_column", 
            "Friendly Name", "Description", "Notes"
        ]
        df = pd.DataFrame(columns=columns)
        #print(f"File {fileName} does not exist. An empty dataframe is created.")

    # Return the dataframe
    return df


def save_file_with_timestamp(fileName, directoryName):
    # Ensure the directory exists
    if not os.path.exists(directoryName):
        os.makedirs(directoryName)
        #print(f"The directory {directoryName} was created.")

    # Extract file name and extension
    base_name, file_extension = os.path.splitext(fileName)

    # Generate timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Create the new file name with timestamp
    new_file_name = f"{base_name}_{timestamp}{file_extension}"

    # Create the full path for the new file
    new_file_path = os.path.join(directoryName, new_file_name)

    # Check if the source file exists before attempting to copy
    if os.path.isfile(fileName):
        # Copy the file to the new location with the new name
        shutil.copy2(fileName, new_file_path)
        #print(f"File move to {new_file_path}")
        
    #else:
        #print(f"The file {fileName} does not exist.")


def create_backup_file(fileName):
    # Split the file path into directory, base name, and extension
    file_dir, file_full_name = os.path.split(fileName)
    base_name, file_extension = os.path.splitext(file_full_name)

    # If the file exists, proceed with creating a backup
    if os.path.isfile(fileName):
        # Find the next available backup number
        backup_number = 0
        while True:
            backup_file_name = f"{base_name}_bak{backup_number:03d}{file_extension}"
            backup_file_path = os.path.join(file_dir, backup_file_name)
            if not os.path.isfile(backup_file_path):
                break
            backup_number += 1

        # Copy the file to create a backup
        shutil.copy2(fileName, backup_file_path)
        #print(f"Backup created as {backup_file_path}")
    # else:
    #     print(f"The file {fileName} does not exist.")


# Check if a file is open in Excel
def is_file_open(filename):
    try:
        # Attempt to open the Excel file as a DataFrame
        df = pd.read_excel(filename)
        # If successful, return True
        return False
    except Exception as e:
        # If an exception occurs, print the error and return False
        print(f"An error occurred: {e}")
        return True


def validate_initialMerge_files(fileName):
    # Step 1: Create a Pandas DataFrame from the Excel file
    try:
        df = pd.read_excel(fileName)
    except Exception as e:
        raise Exception("Error reading the Excel file: " + str(e))

    # Step 2: Check that the DataFrame contains all required columns
    required_columns = ['Domain', 'Application', 'Module', 'Data Dictionary File', 'GlossaryTab']
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise Exception(f"The following required columns are missing from the DataFrame: {missing_columns}")

    # Step 3 and 4: Iterate through the values in the "Data Dictionary File" column
    for file in df['Data Dictionary File']:
        # Check if the file exists in the current directory
        try:
            if not os.path.isfile(file):
                # If a file does not exist, return False
                print(f'   {file} listed in {fileName} does not exist.')
                return False
        except Exception as e:
            print(f'   {file} listed in {fileName} caused exception {e}.')
            return False

    # Step 5: If all files exist, return True
    return True


def process_initialMerge_file(fileName):
    # Step 1: Create a Pandas DataFrame from the Excel file
    try:
        df = pd.read_excel(fileName)
    except Exception as e:
        raise Exception(f"Error reading the Excel file: {e}")

    # Step 2 and 3: Iterate through each row in the dataframe
    for index, row in df.iterrows():
        # Call the runMerge() method with row values as parameters
        runMerge(row['Domain'], row['Application'], row['Module'], row['Data Dictionary File'], row['GlossaryTab'])
        time.sleep(1.1)


def delete_backup_files(directory):
    # Construct the search pattern to find all files that contain '_bak'
    search_pattern = os.path.join(directory, '*_bak*')

    # Use glob to find all files that match the pattern
    backup_files = glob.glob(search_pattern)

    # If no backup files found, return without doing anything
    if not backup_files:
        return

    # Iterate over the list of backup files and delete them
    for file_path in backup_files:
        try:
            os.remove(file_path)
            #print(f"Deleted file: {file_path}")
        except OSError as e:
            print(f"Error deleting backup file: {file_path}. Reason: {e}")


def writeFormattedExcelFile(df, fileName, tabName):
    print(f"Writing Formatted Taxonomy Excel file: {fileName}")
    writer = pd.ExcelWriter(fileName)
    workbook = writer.book
    sheet_vals = {}
    dateFormat = workbook.add_format()
    dateFormat.set_num_format('mm/dd/yy')
    datetimeFormat = workbook.add_format()
    datetimeFormat.set_num_format('mm/dd/yy hh:mm')
    numberFormat = workbook.add_format()
    numberFormat.set_num_format('###,###,###,##0;-###,###,###,##0')
    header_format = workbook.add_format({
        'bg_color': '#0070C0',  
        'font_color': '#FFFFFF',
        'bold': True,           
        'text_wrap': False,
        'valign': 'top',
        'align': 'center',
        'border': 1})

    createFormattedSheet(writer, df, tabName, sheet_vals, dateFormat, datetimeFormat, numberFormat, header_format)
    writer.close()


# Table Formatting Methods
def formatMinMax(worksheet, sheet_vals, dateFormat, datetimeFormat, numberFormat):
    name = worksheet.get_name()
    date_criterion = '=(${}2:${}{}="date")'.format(sheet_vals[name+'_type_colLetter'],sheet_vals[name+'_type_colLetter'],str(sheet_vals[name+'_max_rows']))
    datetime_criterion = '=(SEARCH("datetime",${}2:${}{})>0)'.format(sheet_vals[name+'_type_colLetter'],sheet_vals[name+'_type_colLetter'],str(sheet_vals[name+'_max_rows']))
    numeric_criterion = '=(SEARCH("numeric",${}2:${}{})>0)'.format(sheet_vals[name+'_type_colLetter'],sheet_vals[name+'_type_colLetter'],str(sheet_vals[name+'_max_rows']))
    int_criterion = '=(SEARCH("int",${}2:${}{})>0)'.format(sheet_vals[name+'_type_colLetter'],sheet_vals[name+'_type_colLetter'],str(sheet_vals[name+'_max_rows']))
    float_criterion = '=(SEARCH("float",${}2:${}{})>0)'.format(sheet_vals[name+'_type_colLetter'],sheet_vals[name+'_type_colLetter'],str(sheet_vals[name+'_max_rows']))
    worksheet.conditional_format(1, sheet_vals[name+'_minVal_colNum'], sheet_vals[name+'_max_rows'], sheet_vals[name+'_maxVal_colNum'], 
                                {"type": "formula",
                                "criteria": date_criterion,
                                "format": dateFormat
                                })

    worksheet.conditional_format(1, sheet_vals[name+'_minVal_colNum'], sheet_vals[name+'_max_rows'], sheet_vals[name+'_maxVal_colNum'], 
                                {"type": "formula",
                                "criteria": datetime_criterion,
                                "format": datetimeFormat
                                })

    worksheet.conditional_format(1, sheet_vals[name+'_minVal_colNum'], sheet_vals[name+'_max_rows'], sheet_vals[name+'_maxVal_colNum'], 
                                {"type": "formula",
                                "criteria": numeric_criterion,
                                "format": numberFormat
                                })

    worksheet.conditional_format(1, sheet_vals[name+'_minVal_colNum'], sheet_vals[name+'_max_rows'], sheet_vals[name+'_maxVal_colNum'], 
                                {"type": "formula",
                                "criteria": int_criterion,
                                "format": numberFormat
                                })

    worksheet.conditional_format(1, sheet_vals[name+'_minVal_colNum'], sheet_vals[name+'_max_rows'], sheet_vals[name+'_maxVal_colNum'], 
                                {"type": "formula",
                                "criteria": float_criterion,
                                "format": numberFormat
                                })

def createFormattedSheet(theWriter, df, sheetName, sheet_vals, dateFormat, datetimeFormat, numberFormat,header_format):
    # store location values from df
    sheet_vals[sheetName+'_max_rows'] = df.shape[0]-1
    sheet_vals[sheetName+'_max_cols'] = df.shape[1]-1
    if 'Min Value' in df.columns:
        sheet_vals[sheetName+'_minVal_colNum'] = df.columns.get_loc('Min Value')
        sheet_vals[sheetName+'_maxVal_colNum'] = df.columns.get_loc('Max Value')
    if 'TYPE' in df.columns:
        sheet_vals[sheetName+'_type_colLetter'] = chr(df.columns.get_loc('TYPE')+65)
    
    # create sheet
    df.to_excel(theWriter, sheet_name=sheetName, index=False, startrow=1, header=False)
    # format column widths
    for column in df:
        column_length = max(df[column].astype(str).map(len).max(), len(column)) + 5
        if column_length > 30:
            column_length = 30
        col_idx = df.columns.get_loc(column)
        theWriter.sheets[sheetName].set_column(col_idx, col_idx, column_length)
    # format specifics
    if 'Min Value' in df.columns:
        formatMinMax(theWriter.sheets[sheetName], sheet_vals, dateFormat, datetimeFormat, numberFormat)
    if sheetName == TAXONOMY_GLOSSARY:
        filterAndFreeze(theWriter.sheets[sheetName], sheet_vals)
    addFormatedHeader(theWriter.sheets[sheetName], df, header_format)
    return sheet_vals


def filterAndFreeze (worksheet, sheet_vals):
    name = worksheet.get_name()
    worksheet.autofilter(0,0,sheet_vals[name+'_max_rows'],sheet_vals[name+'_max_cols'])
    worksheet.freeze_panes(1,0)


def addFormatedHeader(worksheet, df, hdr_format):
        # Write the column headers with the defined format.
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, hdr_format)


def cleanUpGlossary(dataframe):
    if "IncludeInView" not in dataframe.columns:
        dataframe.insert(11, 'IncludeInView', "Y")
    trim_text_column(dataframe, "Friendly Name")
    trim_text_column(dataframe, "Description")
    trim_text_column(dataframe, "Notes")


def trim_text_column(dataframe, column_name):
    """
    Trims leading and trailing whitespace from all text values in the specified column of the dataframe.
    
    Parameters:
    dataframe (pd.DataFrame): The dataframe containing the text column to be trimmed.
    column_name (str): The name of the column containing text values to be trimmed.
    
    Returns:
    pd.DataFrame: A dataframe identical to the input, but with trimmed text values in the specified column.
    """
    if column_name in dataframe.columns:
        # Apply the strip function to trim whitespace
        dataframe[column_name] = dataframe[column_name].astype(str).str.strip()

    return dataframe


def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description='Command line program parameters.')
    
    # Define expected arguments
    parser.add_argument('-i', '--initialFile', type=str, help='The initial file to be processed.')
    parser.add_argument('-d', '--domain', type=str, help='The domain parameter.')
    parser.add_argument('-a', '--application', type=str, help='The application parameter.')
    parser.add_argument('-m', '--module', type=str, help='The module parameter.')
    parser.add_argument('-dd', '--datadictionaryFile', type=str, help='The data dictionary file to be merged.')

    # Parse arguments
    args = parser.parse_args()

    # Check the mutually exclusive conditions of initialFile and other parameters
    if args.initialFile:
        if any([args.domain, args.application, args.module, args.datadictionaryFile]):
            parser.error('When initialFile is provided, no other parameters are allowed.\n')
        if not args.initialFile.endswith('.xlsx'):
            parser.error('The initial file must be an .xlsx file.\n')
        if not os.path.isfile(args.initialFile):
            parser.error(f'The file {args.initialFile} does not exist.\n')
        if is_file_open(args.initialFile):
            parser.error(f'The file {args.initialFile} is currently open in another application.\n')
        # Call the runInitialMerge method
        runInitialMerge(args.initialFile)

    elif args.datadictionaryFile:
        if not all([args.domain, args.application, args.module]):
            parser.error('When datadictionaryFile is provided, domain, application, and module parameters must also be provided.\n')
        if not args.datadictionaryFile.endswith('.xlsx'):
            parser.error('The data dictionary file must be an .xlsx file.\n')
        if not os.path.isfile(args.datadictionaryFile):
            parser.error(f'The file {args.datadictionaryFile} does not exist.\n')
        if is_file_open(args.datadictionaryFile):
            parser.error(f'The file {args.datadictionaryFile} is currently open in another application.\n')
        # Call the runMerge method
        runMerge(args.domain, args.application, args.module, args.datadictionaryFile, "Glossary")

    else:
        parser.error('Either initialFile or datadictionaryFile must be provided.')

    delete_backup_files(".")

    print("Done.\n")




if __name__ == "__main__":
    main()
