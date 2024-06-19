# # Data Dictionary Tool
# Tool to create a Data Dictionary based upon input of RAW data retrieved from a live database.
# Copyright 2024 - Agree Technologies

#
#   Semi-automatic test execution can be performed as follows:
#       > python .\TestDataDictionaryTool.py

# Import needed libraries
import pandas as pd
import argparse
import glob
import sys
import textwrap
import warnings
import os.path
import datetime
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
import re

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')


# Define constants
dateLastUpdated = '2024.06.19 03:26:34'



def run_tool():
    # #TODO Validate input files
    # - Does each file have required columns?

    # Input all file data
    print("Reading input files...")

    try:
        print(f"  Reading {tableListFile}.")
        tableList = pd.read_excel(tableListFile, dtype=str, keep_default_na=False)
        print(f"  Read {len(tableList)} rows.")
        print(f"  Reading {tableCharsFile}.")
        tableCharacteristics = pd.read_excel(tableCharsFile, keep_default_na=False)
        print(f"  Read {len(tableCharacteristics)} rows.")
    except:
        print("\nERROR: One of the input files is currently open in Excel.  Please close the file(s) and try again.")
        sys.exit()

    numFiles = len(columnStatsFiles)
    for i in range(numFiles):
        print(f"  Reading {columnStatsFiles[i]}.")
        if i==0:
            columnStats = pd.read_excel(columnStatsFiles[i], keep_default_na=False)
        else:
            columnStats = pd.concat([columnStats, pd.read_excel(columnStatsFiles[i])], ignore_index=True)
    print(f"  Read {len(columnStats)} rows.")
    
    # Create lists of tables to be included in the Data Dictionary, and also those excluded.
    print("Create lists of included and excluded tables...")
 
    includedTableList = []
    excludedTableList = []
    for ind in tableList.index:
        if tableList['Include'][ind] == "1":
            includedTableList.append(tableList['TableName'][ind])
        else:
            excludedTableList.append(tableList['TableName'][ind])

    includedTables = pd.DataFrame({'TableName': includedTableList})
    excludedTables = pd.DataFrame({'TableName': excludedTableList})

    print(f"  The Data Dictionary will include entries from {len(includedTableList)} tables and exclude entries from {len(excludedTableList)} tables")

    # Reduce table characteristics to only reference included tables
    includedTableChars = pd.merge(includedTables, tableCharacteristics,  how='left', \
                                        left_on=['TableName'], \
                                        right_on = ['TableName'])

    # Filter out unneeded info from columnStats
    rawNumRows = columnStats.shape[0]
    filteredColumnsStats = columnStats.copy(deep=True)
    indexesToRemove = []
    print("Searching for unneeded info in the input data...")
    for ind in columnStats.index:
        if "DateTableTemplate_" in columnStats['Table Name'][ind] or \
            "LocalDateTable_" in columnStats['Table Name'][ind] or \
            "RowNumber-" in columnStats['Column Name'][ind]:
            indexesToRemove.append(ind)        

    print(f"Filtering out {len(indexesToRemove)} rows from the raw Column Statistics...")
    filteredColumnsStats.drop(indexesToRemove, axis='index', inplace=True)
    numRowsfilteredColumnsStats = filteredColumnsStats.shape[0]
    print(f"  {rawNumRows - numRowsfilteredColumnsStats} Rows have been filtered from the Column Statistics")

    # Combine Table Characteristics info and Filtered Column Stats to become the Glossary
    print("Creating Glossary...")
    glossary = pd.merge(includedTableChars, filteredColumnsStats, how='left', \
                                        left_on=['TableName','ColumnName'], \
                                        right_on = ['Table Name','Column Name'])
    glossary = glossary.drop(['Table Name', 'Column Name', 'DataType'],axis=1)

    glossary = glossary.rename(columns={'TableName': 'TABLENAME', \
                                        'ColumnName': 'COLNAME', \
                                        'SourceDataType': 'TYPE', \
                                        'Length': 'LEN', \
                                        'Min': 'Min Value', \
                                        'Max': 'Max Value' })

    glossary = glossary.sort_values(by=['TABLENAME', 'COLNAME'], ascending=[True, True], key=lambda x: x.str.lower())

    print(f"  Glossary created with {len(glossary.index)} rows.")

    # Bring in Table Descriptions if the file exists.
    if len(tableDescriptionFile) > 0:
        print("Adding Table descriptions...")
        print(f"  Reading in Table description from: {tableDescriptionFile}")

        try:
            tableDescriptions = pd.read_excel(tableDescriptionFile, sheet_name='Table Descriptions', dtype=str, keep_default_na=False)
        except Exception as e:
            if "Permission denied" in str(e):
                print(f"\nERROR: {tableDescriptionFile} is currently open in Excel.  Please close the file and try again.")
            else:
                print(f"\nERROR: Opening {tableDescriptionFile} raised an error:  {str(e)}")
            sys.exit()

        includedTables = pd.merge(includedTables, tableDescriptions, how = 'left', \
                                        left_on=['TableName'], \
                                        right_on = ['TableName'])    
        numTableDescriptions = includedTables['TableName'].count() - sum(includedTables['Description'].isnull())
        if numTableDescriptions > 0:
            print(f"  {numTableDescriptions} Table descriptions have been added.")
        else:
            print(f"  Warning: Zero Table descriptions were added. Please check the description file to make sure it contains valid data.")

        print("Adding Column descriptions...")
        print(f"  Reading in Column description from: {tableDescriptionFile}")

        try:
            columnDescriptions = pd.read_excel(tableDescriptionFile, sheet_name='Column Descriptions', dtype=str, keep_default_na=False)
        except Exception as e:
            if "Permission denied" in str(e):
                print(f"\nERROR: {tableDescriptionFile} is currently open in Excel.  Please close the file and try again.")
            else:
                print(f"\nERROR: Opening {tableDescriptionFile} raised an error:  {str(e)}")
            sys.exit()
        
        glossary = pd.merge(glossary, columnDescriptions, how = 'left', \
                                        left_on=['TABLENAME','COLNAME'], \
                                        right_on = ['TableName','ColumnName'])
        
        glossary = glossary.drop(['TableName', 'ColumnName'],axis=1)
        numColumnDescriptions = glossary['TABLENAME'].count() - sum(glossary['Description'].isnull())
        if numColumnDescriptions > 0:
            print(f"  {numColumnDescriptions} Column descriptions have been added.")
        else:
            print(f"  Warning: Zero Column descriptions were added. Please check the description file to make sure it contains valid data.")
    else:
        print("Adding empty Description column to Tables and Glossary tabs...")
        glossary = glossary.reindex(columns = glossary.columns.tolist() + ['Friendly Name'])
        glossary = glossary.reindex(columns = glossary.columns.tolist() + ['Description'])
        includedTables = includedTables.reindex(columns = includedTables.columns.tolist() + ['Description'])


    def reorder_dataframe_columns(df, column_order):
        """
        Reorder the columns of a DataFrame according to a given list.
        
        Parameters:
        - df: Pandas DataFrame to be reordered.
        - column_order: List of column names in the desired order.
        
        Returns:
        - DataFrame with columns in the specified order if all columns are found,
        otherwise returns the original DataFrame unchanged.
        """
        # Check if all columns in column_order are in the DataFrame
        if not all(column in df.columns for column in column_order):
            # If not all column names are present, print a warning and return the original DataFrame
            print("Warning: Not all columns in the provided column order list are in the DataFrame.  Column order is unchanged.")
            return df
        else:
            # All columns are present, so reorder and return the new DataFrame
            return df[column_order]


    # Table Formatting Methods
    def formatMinMax(worksheet):
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

    def createFormattedSheet(theWriter, df, sheetName):
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
            if column_length > 40:
                column_length = 40
            col_idx = df.columns.get_loc(column)
            theWriter.sheets[sheetName].set_column(col_idx, col_idx, column_length)
        # format specifics
        if 'Min Value' in df.columns:
            formatMinMax(theWriter.sheets[sheetName])
        if sheetName == 'Glossary':
            filterAndFreeze(theWriter.sheets[sheetName])
        addFormatedHeader(theWriter.sheets[sheetName], df, header_format)

    def filterAndFreeze (worksheet):
        name = worksheet.get_name()
        worksheet.autofilter(0,0,sheet_vals[name+'_max_rows'],sheet_vals[name+'_max_cols'])
        worksheet.freeze_panes(1,0)
    
    def addLinks (worksheet, df):
        idx = 2
        for table in df['TableName']:
            worksheet.write_url('A'+str(idx), "internal:'Table "+table+"'!A1:A1", string=table)
            idx += 1

    def addFormatedHeader(worksheet, df, hdr_format):
         # Write the column headers with the defined format.
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, hdr_format)
       
    def createAboutContent():
        current_time = datetime.datetime.now()
        print(f"Current time: {str(current_time)}")
        aboutDf = pd.DataFrame({'About DataDictionaryTool': [
            "This data dictionary was created on " + str(current_time),
            "DataDictionaryTool version: dateLastUpdated = " + dateLastUpdated]})
        return aboutDf


    #Reorder columns in the Glossary.
    new_col_order = ['TABLENAME', 'COLNAME', 'TYPE', 'LEN', 'Min Value', 'Max Value', 'Cardinality', 'Max Length', 
                     'IsPrimaryKey', 'PK_name', 'PK_ordinal_position', 'IsForeignKey', 'FK_name', 'FK_referenced_table', 'FK_referenced_column', 
                     'Friendly Name', 'Description']
    glossary = reorder_dataframe_columns(glossary, new_col_order)

    # Create Data Dictionary Excel file
    print(f"Writing Data Dictionary Excel file: {dataDictionaryFile}")
    writer = pd.ExcelWriter(dataDictionaryFile)
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

    createFormattedSheet(writer, includedTables, 'Tables')
    createFormattedSheet(writer, glossary, 'Glossary')
    createFormattedSheet(writer, tableList, '_Full Table List')
    createFormattedSheet(writer, excludedTables, '_Excluded Tables')
    createFormattedSheet(writer, tableCharacteristics, '_rawTableChars')
    createFormattedSheet(writer, columnStats, '_rawColumnStats')

    createFormattedSheet(writer, createAboutContent(), 'About')

    writer.close()
    print("Done")





if __name__ == '__main__':
    print("Welcome to the Data Dictionary Tool")
    errorMessage = ''

    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(
            description='Data Dictionary creation tool.',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=textwrap.dedent('''\
                Additional information:
                    Simple operation: Use database parameter only. 
                        Use this when the input files follow the naming convention
                            <database>_ListOfTables.xlsx
                            <database>_TableChars.xlsx      
                            <database>_ColumnStats*.xlsx
                        Output file created: <database>_DataDictionary_working.xlsx
                    Custom operation: 
                        Specify file name parameters when naming convention is not followed. 
                        Do not specify database param.
                        Params tableList, tableChars, columnStatusRoot must match input file.
                        You must provide DDFile param.
                                   
                    Reference:
                        Standardized SQL Queries are saved here:
                        https://inl.sharepoint.com/:f:/r/sites/GRP-AgreeDataAssessmentTeam/Shared%20Documents/General/Data%20Modeling/SQL_queries
                            List of tables: SQLServer_list_of_tables_to_include.sql
                            Table characteristics: SQLServer_table_characteristics.sql
                '''))
        parser.add_argument('--database', type=str, default=None, help='Simple operation: Database name used for input file naming convention.')
        parser.add_argument('--tableList', type=str, default= None, help='Custom operation: Excel file name for the list of tables.')
        parser.add_argument('--tableChars', type=str, default = None, help='Custom operation: Excel file name for table characteristics data.')
        parser.add_argument('--columnStatsRoot', type=str, default = None, help='Custom operation: Base name for the Excel files for column statistics.')
        parser.add_argument('--tableDescriptions', type=str, default = None, help='Custom operation: File containing textual descriptions for tables.')
        parser.add_argument('--DDFile', type=str, default = None, help='Custom operation: Output file name.')
        
        args = parser.parse_args()

        tableListFile = args.tableList
        tableCharsFile = args.tableChars
        tableDescriptionFile = args.tableDescriptions
        
        if tableDescriptionFile is None and args.database is None:
            print("Warning: Table Descriptions file is not specified.  No descriptions will be added to the Data Dictionary.")
            tableDescriptionFile = ""

        if args.columnStatsRoot is not None:
            columnStatsFiles = glob.glob(args.columnStatsRoot + '*.xlsx')
            if len(columnStatsFiles) <= 0:
                errorMessage = "Error finding columnStats file(s).  Check file names against columnStatsRoot param value ({}).".format(args.columnStatsRoot)
                errorMessage += "\nNo files matching {}*.xlsx were found.".format(args.database)

        dataDictionaryFile = args.DDFile

        #Option#
        if args.database is not None:
            tableListFile = args.database + '_ListOfTables.xlsx'
            tableCharsFile = args.database + '_TableChars.xlsx'
            columnStatsFiles = glob.glob(args.database + '_ColumnStats*.xlsx')
            tableDescriptionFile = args.database + '_Descriptions.xlsx'
            dataDictionaryFile = args.database + '_DataDictionary_working.xlsx'
        else:
            if args.DDFile is None:
                errorMessage = "\nError.  Missing DDFile or database param."
                errorMessage += "\nEither the DDFile param or the database param must be specified."

        if len(columnStatsFiles) <= 0:
            errorMessage = "\nError finding columnStats file(s).  Check file names against database param value ({}).".format(args.database)
            errorMessage += "\nNo files matching {}_ColumnStats*.xlsx were found.".format(args.database)

        if not os.path.isfile(tableListFile):
            errorMessage += "\nError: Table List File {} is not found.".format(tableListFile)
        if not os.path.isfile(tableCharsFile):
            errorMessage += "\nError: Table Characteristics File {} is not found.".format(tableCharsFile)

        if tableDescriptionFile != "" :
            if not os.path.isfile(tableDescriptionFile):
                print("Warning: Table Descriptions file is not found.  No descriptions will be added to the Data Dictionary.")
                tableDescriptionFile = ''
            else: 
                print(f"Table Descriptions file ({tableDescriptionFile}) is present and will be used to add table descriptions.")

        if dataDictionaryFile is not None:
            outputFileNumber = 0
            while os.path.isfile(dataDictionaryFile):
                currentDataDictFile = dataDictionaryFile
                outputFileNumber += 1
                fileNameParts = dataDictionaryFile.split(".")
                if outputFileNumber == 1:
                    baseFileName = fileNameParts[0]
                else:
                    baseFileName = fileNameParts[0][:-1]
                dataDictionaryFile = baseFileName + str(outputFileNumber) + "." + fileNameParts[1]
            if outputFileNumber != 0:
                print(f"Output file specified ({currentDataDictFile}) already exists. Output file to be created will be {dataDictionaryFile}.")

        if len(errorMessage) == 0:
            run_tool()
        else:
            print(errorMessage)
    else:
        print(f"Data Dictionary Creation tool. Last updated {dateLastUpdated}.")
        print("Use -h or --help to show detailed usage.")

