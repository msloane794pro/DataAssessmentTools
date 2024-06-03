# # Black-box Test harness for the Data Dictionary Tool
# 
# Simply run this file, and it will extract all necessary test data,
# run the Data Dictionary Tool, and perform validation on the output.
# Copyright 2024 - Agree Technologies

# Import needed libraries
import os
import shutil
import glob
import time
from pathlib import Path
import pandas as pd

# Global variables

program = os.path.abspath(__file__)
pwd = os.path.dirname(program)
testDataDir = os.path.abspath('TestData')
testFileGroups = ['Database1']
outputDDsubstring1 = '_DataDictionary_working.xlsx'
outputDDsubstring2 = '_DataDictionary_working1.xlsx'

# Initialize
def init():
    tprint('Initializing the test environment.')

# Setup Test Environment

#   1. Copy test data to this directory
def copyTestData():
    tprint("Copying test data files.")
    tprint(f'Current working directory: {pwd}')
    tprint(f'Test data directory: {testDataDir}')
    
    for i, group in enumerate(testFileGroups):
        #tprint(f'{i} - Test file group: {group}')
        for file in glob.glob(f'{testDataDir}/{group}*.dat'):
            #tprint(f'Copying {file}')
            shutil.copy(file, pwd)
            

#   2. Rename test data files
def renameTestFiles():
    tprint("Renaming test data files.")
    for i, group in enumerate(testFileGroups):
        #tprint(f'{i} - Test file group: {group}')
        for file in glob.glob(f'{pwd}/{group}*.dat'):
            newFile = file.replace('.dat','.xlsx')
            #tprint(f'Renaming {file} to \n      {newFile}')
            os.rename(file, newFile)


#   3. Execute Tests

# Test Case 1 - Run with no command line options.
def executeTool1(message):
    tprint(message)
    with open("DataDictionaryTool.py") as f:
        exec(f.read())

# Test Case 2 - Run with -h command line option.
def executeTool2(message):
    tprint(message)
    os.system("python DataDictionaryTool.py -h")

# Test Case 3 - Run with --database command line option.
def executeTool3(message):
    tprint(message)
    os.system(f'python DataDictionaryTool.py --database {testFileGroups[0]}')

# -- Examine and validate the output from the tool.
# ---- Output file exists?
def validateFileExists1(valId):
    expectedOutputFile = f'{testFileGroups[0]}_DataDictionary_working.xlsx'
    if Path(expectedOutputFile).exists():
        tprint(f'Validation {valId} - Pass - Correctly named output file exists: {expectedOutputFile}')
    else:
        raise Exception(f'Validation {valId} - FAIL - Correctly named output file not found.  Expected {expectedOutputFile}')

def validateFileContainsWorksheets(valId):
    expectedOutputFile = f'{testFileGroups[0]}_DataDictionary_working.xlsx'
    try:
        observedDf = pd.read_excel(expectedOutputFile, sheet_name='Tables', dtype=str, keep_default_na=False)
        observedDf = pd.read_excel(expectedOutputFile, sheet_name='Glossary', dtype=str, keep_default_na=False)
        observedDf = pd.read_excel(expectedOutputFile, sheet_name='_Full Table List', dtype=str, keep_default_na=False)
        observedDf = pd.read_excel(expectedOutputFile, sheet_name='_Excluded Tables', dtype=str, keep_default_na=False)
        observedDf = pd.read_excel(expectedOutputFile, sheet_name='_rawTableChars', dtype=str, keep_default_na=False)
        observedDf = pd.read_excel(expectedOutputFile, sheet_name='_rawColumnStats', dtype=str, keep_default_na=False)
        observedDf = pd.read_excel(expectedOutputFile, sheet_name='About', dtype=str, keep_default_na=False)
        tprint(f'Validation {valId} - Pass - All expected worksheets were found in {expectedOutputFile}')
    except Exception as e:
        raise Exception (f'Validation {valId} - FAIL - Expected worksheet not found. {str(e)}')

def validateTablesWs(valId):
    expectedOutputFile = f'{testFileGroups[0]}_DataDictionary_working.xlsx'
    observedDf = pd.read_excel(expectedOutputFile, sheet_name='Tables', dtype=str, keep_default_na=False)

    expectedLen = 3
    if len(observedDf) != expectedLen:
        raise Exception (f'Validation {valId} - FAIL - Tables worksheet length is incorrect. Expected: {expectedLen}; Observed: {len(observedDf)}')
    
    if len(observedDf.columns) < 2:
        raise Exception (f'Validation {valId} - FAIL - Incorrect number of column in Tables worksheet. Expected: 2 or more; Observed: {len(observedDf.columns)}')

    expectedCols = ['TableName', 'Description']
    if observedDf.columns[0] != expectedCols[0]:
        raise Exception (f'Validation {valId} - FAIL - Incorrect column in Tables worksheet. Expected: {expectedCols[0]}; Observed: {observedDf.columns[0]}')
    if observedDf.columns[1] != expectedCols[1]:
        raise Exception (f'Validation {valId} - FAIL - Incorrect column in Tables worksheet. Expected: {expectedCols[1]}; Observed: {observedDf.columns[1]}')

    tprint(f'Validation {valId} - Pass - Tables worksheet constructed correctly in {expectedOutputFile}')

def validateTablesWsValues(valId):
    expectedOutputFile = f'{testFileGroups[0]}_DataDictionary_working.xlsx'
    observedDf = pd.read_excel(expectedOutputFile, sheet_name='Tables', dtype=str, keep_default_na=False)
    assertEquals('bTable', observedDf.iloc[0]['TableName'], valId)
    assertEquals('dTable', observedDf.iloc[1]['TableName'], valId)
    assertEquals('rTable', observedDf.iloc[2]['TableName'], valId)
    assertEquals('Bluberries', observedDf.iloc[0]['Description'], valId)
    assertEquals('Deli sandwiches', observedDf.iloc[1]['Description'], valId)
    assertEquals('Red garden tomatos', observedDf.iloc[2]['Description'], valId)
    tprint(f'Validation {valId} - Pass - Tables worksheet values are all correct in {expectedOutputFile}')

def validateGlossaryColumns(valId):
    expectedOutputFile = f'{testFileGroups[0]}_DataDictionary_working.xlsx'
    observedDf = pd.read_excel(expectedOutputFile, sheet_name='Glossary', dtype=str, keep_default_na=False)

    expectedCols = ['TABLENAME', 'COLNAME', 'TYPE', 'LEN', 'Min Value', 'Max Value', 'Cardinality', 'Max Length', 'Friendly Name', 'Description']

    assertEquals(expectedCols[0], observedDf.columns[0], valId)
    assertEquals(expectedCols[1], observedDf.columns[1], valId)
    assertEquals(expectedCols[2], observedDf.columns[2], valId)
    assertEquals(expectedCols[3], observedDf.columns[3], valId)
    assertEquals(expectedCols[4], observedDf.columns[4], valId)
    assertEquals(expectedCols[5], observedDf.columns[5], valId)
    assertEquals(expectedCols[6], observedDf.columns[6], valId)
    assertEquals(expectedCols[7], observedDf.columns[7], valId)
    assertEquals(expectedCols[8], observedDf.columns[8], valId)
    assertEquals(expectedCols[9], observedDf.columns[9], valId)

    tprint(f'Validation {valId} - Pass - Glossary Columns are all correct in {expectedOutputFile}')

def validateGlossaryLength(valId):
    expectedOutputFile = f'{testFileGroups[0]}_DataDictionary_working.xlsx'
    observedDf = pd.read_excel(expectedOutputFile, sheet_name='Glossary', dtype=str, keep_default_na=False)

    expectedLen = 252

    assertEquals(expectedLen, len(observedDf), valId)

    tprint(f'Validation {valId} - Pass - Glossary Length is correct in {expectedOutputFile}')

def validateGlossaryTableNames(valId):
    expectedOutputFile = f'{testFileGroups[0]}_DataDictionary_working.xlsx'
    observedDf = pd.read_excel(expectedOutputFile, sheet_name='Glossary', dtype=str, keep_default_na=False)

    expectedTableNames = ['bTable', 'dTable', 'rTable']

    allValidTables = True
    tableName0count = 0
    tableName1count = 0
    tableName2count = 0

    for ind in observedDf.index:
        if observedDf['TABLENAME'][ind] not in expectedTableNames:
            tprint(f'{valId} - Unexpected Table Name observed: {observedDf["TABLENAME"][ind]}')
            allValidTables = False
            break
        if observedDf['TABLENAME'][ind] == expectedTableNames[0]:
            tableName0count += 1
        if observedDf['TABLENAME'][ind] == expectedTableNames[1]:
            tableName1count += 1
        if observedDf['TABLENAME'][ind] == expectedTableNames[2]:
            tableName2count += 1

    assertEquals(True, allValidTables, valId)
    assertEquals(139, tableName0count, valId)
    assertEquals(37, tableName1count, valId)
    assertEquals(76, tableName2count, valId)

    tprint(f'Validation {valId} - Pass - Glossary Table Names are all correct in {expectedOutputFile}')

def validateGlossaryColumnNames(valId):
    expectedOutputFile = f'{testFileGroups[0]}_DataDictionary_working.xlsx'
    observedDf = pd.read_excel(expectedOutputFile, sheet_name='Glossary', dtype=str, keep_default_na=False)

    # Construct a list containing the column names that are observed.
    observedColumnNames = []
    for ind in observedDf.index:
        tableAndColumn = f'{observedDf["TABLENAME"][ind]}-{observedDf["COLNAME"][ind]}'
        if tableAndColumn in observedColumnNames:
            raise Exception (f'{valId} - FAIL - Duplicate column name observed: {tableAndColumn}')
        observedColumnNames.append(tableAndColumn)

    assertEquals(len(observedColumnNames), 252, str(f'{valId} - Column Count'))
        
    # Verify expected column names are in the list.
    assertEquals('zTable-zz_id' in observedColumnNames, False, str(f'{valId}'))
    assertEquals('bTable-ac_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-ac_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-address1' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-address2' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-age' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_avg_em' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_avg_floor' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_bl_comn_gp' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_bl_comn_nocup' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_bl_comn_ocup' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_bl_comn_rm' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_bl_comn_serv' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_em_dp' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_ext_wall' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_gp' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_gp_comn' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_gp_dp' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_gross_ext' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_gross_int' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_ls_negotiated' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_nocup' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_nocup_comn' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_nocup_dp' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_ocup' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_ocup_comn' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_ocup_dp' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_remain' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_rentable' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_rm' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_rm_comn' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_rm_dp' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_serv' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_su' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_usable' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-area_vert_pen' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-auto_est_balance_points' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-bl_cat' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-bl_ci' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-bl_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-bl_num' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-bl_number' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-bl_status' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-bl_status_year' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-bl_use_val' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-bldg_photo' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-campus' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-campus_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-city_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-comment_disposal' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-comments' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-company_code' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-complex_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-condition' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-construction_type' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-construction_type_val' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-contact_email' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-contact_name' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-contact_phone' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-cooling_balance_point' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-cooling_balance_point_manual' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-cost_operating_total' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-cost_other_total' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-cost_replace' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-cost_sqft' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-cost_tax_total' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-cost_utility_total' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-count_em' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-count_fl' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-count_ls' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-count_max_occup' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-count_occup' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-criticality' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-ctry_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-date_bl' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-date_book_val' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-date_costs_end' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-date_costs_last_calcd' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-date_costs_start' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-date_disposal' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-date_market_val' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-date_rehab' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-detail_dwg' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-disposal_type' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-dwgname' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-ehandle' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-em_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-emp_count' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-energy_baseline_year' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-fasb_ls_type' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-geo_objectid' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-grp_uid' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-heating_balance_point' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-heating_balance_point_manual' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-image_file' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-income_total' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-is_bl_addacc' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-is_bl_hist' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-is_bl_hsecurity' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-is_child_occupied' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-lat' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-legal_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-lon' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-name' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-occup_target' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-option1' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-option2' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-pending_action' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-perimeter' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-pr_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-qty_life_expect' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-ratio_ru' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-ratio_ur' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-regn_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-site_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-social_distance' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-source_date_update' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-source_feed_comments' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-source_record_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-source_status' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-source_system_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-source_table' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-source_time_update' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-stat_life_remain' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-state_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-status' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-std_area_per_em' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-structure_type' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-use1' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-utility_type_cool' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-utility_type_heat' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-uuid' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-value_bldg' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-value_book' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-value_deprec_remain' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-value_extras' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-value_land' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-value_market' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-weather_source_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-weather_station_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('bTable-zip' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-admin_email' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-admin_phone' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-approving_mgr' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-area_avg_em' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-area_chargable' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-area_comn' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-area_comn_gp' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-area_comn_nocup' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-area_comn_ocup' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-area_comn_rm' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-area_comn_serv' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-area_gp' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-area_nocup' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-area_ocup' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-area_rm' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-area_rm_personnel' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-area_second_circ' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-company_code' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-cost' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-count_em' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-dp_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-dv_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-em_area_chargable' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-em_area_comn' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-em_area_comn_rm' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-em_area_comn_serv' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-em_area_rm' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-em_cost' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-head' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-hpattern' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-hpattern_acad' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-is_directorate_hoteler' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-name' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-option1' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-option2' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-source_record_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('dTable-uuid' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-ac_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-area' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-area_alloc' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-area_chargable' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-area_comn' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-area_comn_nocup' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-area_comn_ocup' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-area_comn_rm' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-area_comn_serv' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-area_manual' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-area_unalloc' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-bl_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-cap_em' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-cap_em_target' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-ceiling_height' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-cost' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-cost_sqft' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-count_em' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-date_last_surveyed' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-dp_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-dv_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-dwgname' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-ehandle' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-extension' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-fl_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-geo_objectid' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-home_org' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-hotelable' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-inel_dirty_flag' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-inel_multi_use_1' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-inel_multi_use_10' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-inel_multi_use_11' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-inel_multi_use_12' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-inel_multi_use_13' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-inel_multi_use_2' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-inel_multi_use_3' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-inel_multi_use_4' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-inel_multi_use_5' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-inel_multi_use_6' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-inel_multi_use_7' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-inel_multi_use_8' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-inel_multi_use_9' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-inl_dir' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-inl_dv' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-lab_data' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-lat' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-layer_name' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-length' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-length_manual' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-lon' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-ls_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-name' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-option1' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-option2' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-org_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-phone' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-prorate' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-recovery_status' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-reservable' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-rm_cat' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-rm_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-rm_photo' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-rm_std' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-rm_type' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-rm_use' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-rm_zone' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-source_record_id' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-status' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-survey_comments_rm' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-survey_photo' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-survey_redline_rm' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-tc_level' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-time_last_surveyed' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-transfer_status' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-uuid' in observedColumnNames, True, str(f'{valId}'))
    assertEquals('rTable-width_manual' in observedColumnNames, True, str(f'{valId}'))

    tprint(f'Validation {valId} - Pass - Glossary Column names are all correct in {expectedOutputFile}')

def validateGlossaryDataTypes(valId):
    expectedOutputFile = f'{testFileGroups[0]}_DataDictionary_working.xlsx'
    observedDf = pd.read_excel(expectedOutputFile, sheet_name='Glossary', dtype=str, keep_default_na=False)

    # Construct a dictionary containing the number of times each data type is observed.
    observedDataTypes = {}
    for ind in observedDf.index:
        if observedDf["TYPE"][ind] not in observedDataTypes.keys():
            observedDataTypes.update({observedDf["TYPE"][ind]: 1})
        else:
            incValue = observedDataTypes.get(observedDf["TYPE"][ind]) + 1
            observedDataTypes.update({observedDf["TYPE"][ind]: incValue})

    # Iterate through dictionary and assert on expected values
    for key in observedDataTypes:
        match key:
            case 'char(1)':
                dtype = 'char(1)'
                assertEquals(observedDataTypes.get(dtype), 3, str(f'{valId} - {dtype}'))
            case 'char(10)':
                dtype = 'char(10)'
                assertEquals(observedDataTypes.get(dtype), 4, str(f'{valId} - {dtype}'))
            case 'char(12)':
                dtype = 'char(12)'
                assertEquals(observedDataTypes.get(dtype), 3, str(f'{valId} - {dtype}'))
            case 'char(16)':
                dtype = 'char(16)'
                assertEquals(observedDataTypes.get(dtype), 14, str(f'{valId} - {dtype}'))
            case 'char(20)':
                dtype = 'char(20)'
                assertEquals(observedDataTypes.get(dtype), 2, str(f'{valId} - {dtype}'))
            case 'char(24)':
                dtype = 'char(24)'
                assertEquals(observedDataTypes.get(dtype), 6, str(f'{valId} - {dtype}'))
            case 'char(25)':
                dtype = 'char(25)'
                assertEquals(observedDataTypes.get(dtype), 1, str(f'{valId} - {dtype}'))
            case 'char(255)':
                dtype = 'char(255)'
                assertEquals(observedDataTypes.get(dtype), 1, str(f'{valId} - {dtype}'))
            case 'char(32)':
                dtype = 'char(32)'
                assertEquals(observedDataTypes.get(dtype), 11, str(f'{valId} - {dtype}'))
            case 'char(36)':
                dtype = 'char(36)'
                assertEquals(observedDataTypes.get(dtype), 8, str(f'{valId} - {dtype}'))
            case 'char(4)':
                dtype = 'char(4)'
                assertEquals(observedDataTypes.get(dtype), 6, str(f'{valId} - {dtype}'))
            case 'char(5)':
                dtype = 'char(5)'
                assertEquals(observedDataTypes.get(dtype), 1, str(f'{valId} - {dtype}'))
            case 'char(50)':
                dtype = 'char(50)'
                assertEquals(observedDataTypes.get(dtype), 13, str(f'{valId} - {dtype}'))
            case 'char(6)':
                dtype = 'char(6)'
                assertEquals(observedDataTypes.get(dtype), 1, str(f'{valId} - {dtype}'))
            case 'char(64)':
                dtype = 'char(64)'
                assertEquals(observedDataTypes.get(dtype), 15, str(f'{valId} - {dtype}'))
            case 'char(7)':
                dtype = 'char(7)'
                assertEquals(observedDataTypes.get(dtype), 1, str(f'{valId} - {dtype}'))
            case 'char(8)':
                dtype = 'char(8)'
                assertEquals(observedDataTypes.get(dtype), 6, str(f'{valId} - {dtype}'))
            case 'datetime':
                dtype = 'datetime'
                assertEquals(observedDataTypes.get(dtype), 12, str(f'{valId} - {dtype}'))
            case 'int':
                dtype = 'int'
                assertEquals(observedDataTypes.get(dtype), 14, str(f'{valId} - {dtype}'))
            case 'numeric(10, 2)':
                dtype = 'numeric(10, 2)'
                assertEquals(observedDataTypes.get(dtype), 4, str(f'{valId} - {dtype}'))
            case 'numeric(12, 1)':
                dtype = 'numeric(12, 1)'
                assertEquals(observedDataTypes.get(dtype), 8, str(f'{valId} - {dtype}'))
            case 'numeric(12, 2)':
                dtype = 'numeric(12, 2)'
                assertEquals(observedDataTypes.get(dtype), 60, str(f'{valId} - {dtype}'))
            case 'numeric(16, 8)':
                dtype = 'numeric(16, 8)'
                assertEquals(observedDataTypes.get(dtype), 4, str(f'{valId} - {dtype}'))
            case 'numeric(22, 2)':
                dtype = 'numeric(22, 2)'
                assertEquals(observedDataTypes.get(dtype), 1, str(f'{valId} - {dtype}'))
            case 'numeric(4, 2)':
                dtype = 'numeric(4, 2)'
                assertEquals(observedDataTypes.get(dtype), 1, str(f'{valId} - {dtype}'))
            case 'numeric(6, 2)':
                dtype = 'numeric(6, 2)'
                assertEquals(observedDataTypes.get(dtype), 4, str(f'{valId} - {dtype}'))
            case 'numeric(7, 2)':
                dtype = 'numeric(7, 2)'
                assertEquals(observedDataTypes.get(dtype), 7, str(f'{valId} - {dtype}'))
            case 'numeric(8, 2)':
                dtype = 'numeric(8, 2)'
                assertEquals(observedDataTypes.get(dtype), 6, str(f'{valId} - {dtype}'))
            case 'numeric(9, 1)':
                dtype = 'numeric(9, 1)'
                assertEquals(observedDataTypes.get(dtype), 2, str(f'{valId} - {dtype}'))
            case 'numeric(9, 2)':
                dtype = 'numeric(9, 2)'
                assertEquals(observedDataTypes.get(dtype), 2, str(f'{valId} - {dtype}'))
            case 'smallint':
                dtype = 'smallint'
                assertEquals(observedDataTypes.get(dtype), 12, str(f'{valId} - {dtype}'))
            case 'varchar(1000)':
                dtype = 'varchar(1000)'
                assertEquals(observedDataTypes.get(dtype), 1, str(f'{valId} - {dtype}'))
            case 'varchar(128)':
                dtype = 'varchar(128)'
                assertEquals(observedDataTypes.get(dtype), 4, str(f'{valId} - {dtype}'))
            case 'varchar(20)':
                dtype = 'varchar(20)'
                assertEquals(observedDataTypes.get(dtype), 1, str(f'{valId} - {dtype}'))
            case 'varchar(256)':
                dtype = 'varchar(256)'
                assertEquals(observedDataTypes.get(dtype), 1, str(f'{valId} - {dtype}'))
            case 'varchar(36)':
                dtype = 'varchar(36)'
                assertEquals(observedDataTypes.get(dtype), 2, str(f'{valId} - {dtype}'))
            case 'varchar(5000)':
                dtype = 'varchar(5000)'
                assertEquals(observedDataTypes.get(dtype), 2, str(f'{valId} - {dtype}'))
            case 'varchar(64)':
                dtype = 'varchar(64)'
                assertEquals(observedDataTypes.get(dtype), 6, str(f'{valId} - {dtype}'))
            case 'varchar(90)':
                dtype = 'varchar(90)'
                assertEquals(observedDataTypes.get(dtype), 2, str(f'{valId} - {dtype}'))
            case _:
                raise Exception (f'{valId} - FAIL - Unexpected data type observed: {str(key)}')

    tprint(f'Validation {valId} - Pass - Glossary Data Types are all correct in {expectedOutputFile}')


def validateGlossaryDescriptionQuantity(valId):
    expectedOutputFile = f'{testFileGroups[0]}_DataDictionary_working.xlsx'
    observedDf = pd.read_excel(expectedOutputFile, sheet_name='Glossary', dtype=str, keep_default_na=False)

    expectedQty = 236 # 252
    observedQty = 0
    for ind in observedDf.index:
        if observedDf["Description"][ind]  != '':
            observedQty += 1

    assertEquals(expectedQty, observedQty, valId)

    tprint(f'Validation {valId} - Pass - Glossary Length is correct in {expectedOutputFile}')

def validateGlossaryValuesSparse(valId):
    expectedOutputFile = f'{testFileGroups[0]}_DataDictionary_working.xlsx'
    observedDf = pd.read_excel(expectedOutputFile, sheet_name='Glossary', dtype=str, keep_default_na=False)    

    assertEquals('bTable', observedDf["TABLENAME"][3], str(f'{valId} - ["TABLENAME"][3]'))
    assertEquals('bTable', observedDf["TABLENAME"][138], str(f'{valId} - ["TABLENAME"][138]'))
    assertEquals('dTable', observedDf["TABLENAME"][139], str(f'{valId} - ["TABLENAME"][139]'))
    assertEquals('dTable', observedDf["TABLENAME"][140], str(f'{valId} - ["TABLENAME"][140]'))
    assertEquals('dTable', observedDf["TABLENAME"][141], str(f'{valId} - ["TABLENAME"][141]'))
    assertEquals('rTable', observedDf["TABLENAME"][176], str(f'{valId} - ["TABLENAME"][176]'))
    assertEquals('rTable', observedDf["TABLENAME"][251], str(f'{valId} - ["TABLENAME"][251]'))
    assertEquals('area_nocup', observedDf["COLNAME"][19], str(f'{valId} - ["COLNAME"][19]'))
    assertEquals('head', observedDf["COLNAME"][167], str(f'{valId} - ["COLNAME"][167]'))
    assertEquals('cap_em', observedDf["COLNAME"][188], str(f'{valId} - ["COLNAME"][188]'))
    assertEquals('numeric(12, 2)', observedDf["TYPE"][179], str(f'{valId} - ["TYPE"][179]'))
    assertEquals('datetime', observedDf["TYPE"][120], str(f'{valId} - ["TYPE"][120]'))
    assertEquals('smallint', observedDf["TYPE"][70], str(f'{valId} - ["TYPE"][70]'))
    assertEquals('10, 2', observedDf["LEN"][36], str(f'{valId} - ["LEN"][36]'))
    assertEquals('128', observedDf["LEN"][139], str(f'{valId} - ["LEN"][139]'))
    assertEquals('NULL', observedDf["LEN"][175], str(f'{valId} - ["LEN"][175]'))
    assertEquals('45565', observedDf["Min Value"][74], str(f'{valId} - ["Min Value"][74]'))
    assertEquals('ATR COMPLEX', observedDf["Min Value"][112], str(f'{valId} - ["Min Value"][112]'))
    assertEquals('', observedDf["Min Value"][167], str(f'{valId} - ["Min Value"][167]'))
    assertEquals('14 0 7 96', observedDf["Max Value"][169], str(f'{valId} - ["Max Value"][169]'))
    assertEquals('0', observedDf["Max Value"][192], str(f'{valId} - ["Max Value"][192]'))
    assertEquals('WMF-TR-91ST', observedDf["Max Value"][197], str(f'{valId} - ["Max Value"][197]'))
    assertEquals('1', observedDf["Cardinality"][189], str(f'{valId} - ["Cardinality"][189]'))
    assertEquals('2186', observedDf["Cardinality"][223], str(f'{valId} - ["Cardinality"][223]'))
    assertEquals('88', observedDf["Cardinality"][244], str(f'{valId} - ["Cardinality"][244]'))
    assertEquals('', observedDf["Max Length"][0], str(f'{valId} - ["Max Length"][0]'))
    assertEquals('11', observedDf["Max Length"][187], str(f'{valId} - ["Max Length"][187]'))
    assertEquals('28', observedDf["Max Length"][237], str(f'{valId} - ["Max Length"][237]'))
    assertEquals('Room Category', observedDf["Friendly Name"][235], str(f'{valId} - ["Friendly Name"][235]'))
    assertEquals('Employee Count', observedDf["Friendly Name"][85], str(f'{valId} - ["Friendly Name"][85]'))    
    assertEquals('Survey Photo for table rTable', observedDf["Description"][245], str(f'{valId} - ["Description"][245]'))
    assertEquals('Historic Building? for table bTable', observedDf["Description"][95], str(f'{valId} - ["Description"][95]'))

    tprint(f'Validation {valId} - Pass - Sparce spot-checking of Glossary values are all correct in {expectedOutputFile}')

#TODO:
# ----  Conditional formatting of datetime is working as expected?
# ----  Conditional formatting of numeric is working as expected?    


#   Test Case 4 - Rename test data files
def customizeTestFileNames():
    tprint("Customizing test data files to not follow the simplified naming convention.")
    for i, group in enumerate(testFileGroups):
        #tprint(f'{i} - Test file group: {group}')
        for file in glob.glob(f'{pwd}/{group}*.xlsx'):
            if 'RawColumnStats' in str(file):
                newFile = file.replace('RawColumnStats', 'RCS')   
                os.rename(file, newFile)            
            elif 'RawListOfTables' in str(file):
                newFile = file.replace('RawListOfTables', 'RLOT')
                os.rename(file, newFile)
            elif 'RawTableChars' in str(file):
                newFile = file.replace('RawTableChars', 'RTC')
                os.rename(file, newFile)
            elif 'Descriptions' in str(file):
                newFile = file.replace('Descriptions', 'Ignore')
                os.rename(file, newFile)
            
# Test Case 4 - Run with custom file name command line options.
def executeTool4(message):
    tprint(message)
    os.system(f'python DataDictionaryTool.py \
              --tableList {testFileGroups[0]}_RLOT.xlsx \
              --tableChars {testFileGroups[0]}_RTC.xlsx \
              --columnStatsRoot {testFileGroups[0]}_RCS \
              --DDFile {testFileGroups[0]}_DD_working.xlsx \
                ')

# Test Case 6 - Run with AI command line options.
def executeTool6(message):
    tprint(message)
    os.system(f'python DataDictionaryTool.py \
              --tableList {testFileGroups[0]}_RLOT.xlsx \
              --tableChars {testFileGroups[0]}_RTC.xlsx \
              --columnStatsRoot {testFileGroups[0]}_RCS \
              --DDFile {testFileGroups[0]}_DD_working.xlsx \
              -ai \
                ')

# Tear-down Test Environment

#   1. Delete test data files
def deleteTestDataFiles():
    tprint("Cleanup: Deleting test data files.")
    for i, group in enumerate(testFileGroups):
        #tprint(f'{i} - Test file group: {group}')
        for file in glob.glob(f'{pwd}/{group}*.*'):
            #tprint(f'Deleting {file}')
            os.remove(file)


def tprint(message):
    print(f'+++ {message}')


def assertEquals(expected, observed, message):
    if str(observed) != str(expected):
        raise Exception (f'{message} - Assert Equals - FAIL - Expected: {str(expected)}; Observed: {str(observed)}')


if __name__ == '__main__':
    try:
        init()
        copyTestData()
        renameTestFiles()

        # Test Case 1 - Run the script with no command line params.  No validation.  Watch for exceptions only.

        executeTool1('Test Case 1 - Run with no command line options.')


        # Test Case 2 - Run the script with help command line param.  No validation.  Watch for exceptions only.

        executeTool2('Test Case 2 - Run with -h command line options.')


        # Test Case 3 - Simple Operation - with descriptions

        executeTool3('Test Case 3 - Run with --database command line option.')
        
        tprint('\nStarting validations for Test Case 3.')
        validateFileExists1('3.01')
        validateFileContainsWorksheets('3.02')
        validateTablesWs('3.03')
        validateTablesWsValues('3.04')
        validateGlossaryColumns('3.05')
        validateGlossaryLength('3.06')
        validateGlossaryTableNames('3.07')
        validateGlossaryColumnNames('3.08')
        validateGlossaryDataTypes('3.09')
        validateGlossaryDescriptionQuantity('3.10')
        validateGlossaryValuesSparse('3.11')


        # Test Case 4 - Custom Operation - without descriptions

        customizeTestFileNames()
        executeTool4('Test Case 4 - Run with custom file name command line options.')

        # validateFileExists('3.01')
        # validateFileContainsWorksheets('3.02')
        # validateTablesWs('3.03')
        # validateTablesWsValues('3.04')
        # validateGlossaryColumns('3.05')
        # validateGlossaryLength('3.06')
        # validateGlossaryTableNames('3.07')
        # validateGlossaryColumnNames('3.08')
        # validateGlossaryDataTypes('3.09')
        # validateGlossaryDescriptionQuantity2('3.10')
        # validateGlossaryValuesSparse2('3.11')    

        executeTool4('Test Case 5 - Re-Run with the exact same custom file name command line options.')

        # validateFileExists('3.01')

        executeTool6('Test Case 6 - Run with the AI command line options.')

    except Exception as e: tprint(f'!!! EXCEPTION: {e}')
    finally:
        time.sleep(1)
        deleteTestDataFiles()
        tprint('Testing is complete.')
    