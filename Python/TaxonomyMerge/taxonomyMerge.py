import argparse
import os
import sys
import pandas as pd

# Define the methods runInitialMerge and runMerge as placeholders
def runInitialMerge(initialMergeFile):
    print(f'Running initial merge using {initialMergeFile}')
    # Add your merge logic here

def runMerge(domainVal, appVal, moduleVal, ddFile):
    print(f'Running merge:\n   Domain: {domainVal}\n   Application: {appVal}\n   Module: {moduleVal}\n   Data Dictionary file: {ddFile}')
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
        runMerge(args.domain, args.application, args.module, args.datadictionaryFile)

    else:
        parser.error('Either initialFile or datadictionaryFile must be provided.')




if __name__ == "__main__":
    main()
