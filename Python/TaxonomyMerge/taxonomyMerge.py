import argparse
import os
import sys
import pandas as pd
import os
import shutil
from datetime import datetime
import time


# Constants
TAXONOMY_FILE = "TheBigTaxonomyFile.xlsx"
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
    print(f'Running merge:  Domain: {domainVal}, Application: {appVal}, Module: {moduleVal}, Data Dictionary file: {ddFile}, Glossary Tab: {glossaryTab}')

    create_backup_file(TAXONOMY_FILE)

    taxonomy_df = create_taxonomy_df(TAXONOMY_FILE, TAXONOMY_GLOSSARY)

    glossary_df = pd.read_excel(ddFile, sheet_name=glossaryTab)
    glossary_df.insert(0, 'Module', moduleVal)
    glossary_df.insert(0, 'Application', appVal)
    glossary_df.insert(0, 'Domain', domainVal)
    if "IncludeInView" not in glossary_df.columns:
        glossary_df.insert(11, 'IncludeInView', "Y")
    
    updatedTaxonomy_df = append_dataframes(glossary_df, taxonomy_df)

    print(f'...Row counts: Current: {len(taxonomy_df)}, Additional: {len(glossary_df)}, New: {len(updatedTaxonomy_df)}')

    with pd.ExcelWriter(TAXONOMY_FILE, engine='openpyxl') as writer:
        updatedTaxonomy_df.to_excel(writer, sheet_name=TAXONOMY_GLOSSARY, index=False)

    save_file_with_timestamp(TAXONOMY_FILE, ARCHIVE_DIR)


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
        print(f"The directory {directoryName} was created.")

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
        
    else:
        print(f"The file {fileName} does not exist.")


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
    else:
        print(f"The file {fileName} does not exist.")


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
        time.sleep(1.5)



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




if __name__ == "__main__":
    main()
