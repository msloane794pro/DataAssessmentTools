import argparse
import os
import sys
import pandas as pd

# Define the methods runInitialMerge and runMerge as placeholders
def runInitialMerge(initialMergeFile):
    print(f'Running initial merge using {initialMergeFile}')
    if validate_initialMerge_files(initialMergeFile):
        print(f'All data files listed {initialMergeFile} in are present. Ready to process the initial merge.')
        process_initialMerge_file(initialMergeFile)
    else:
        print(f'ERROR: Data files listed {initialMergeFile} are missing.')
    # Add your merge logic here


def runMerge(domainVal, appVal, moduleVal, ddFile, glossaryTab):
    print(f'Running merge:  Domain: {domainVal}, Application: {appVal}, Module: {moduleVal}, Data Dictionary file: {ddFile}, Glossary Tab: {glossaryTab}')
    # Add your merge logic here


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
