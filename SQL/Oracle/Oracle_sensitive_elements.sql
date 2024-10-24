SELECT atc.table_name as "TableName",
       atc.column_name as "ColumnName"
FROM all_tab_columns atc
WHERE atc.OWNER = 'EDMS70'
  AND (
      -- List sub-strings that might indicate the element is sensitive.
      REGEXP_LIKE(atc.column_name, 'password|passcode', 'i')
      
      -- List exact column names that might indicate that the element is sensitive
      OR atc.column_name IN ('PIN', 'SSN')
  )
  -- List the tables to restrict the search to.
  AND atc.table_name IN (
        'DOC_INDEX',
        'DRUI',
        'DRUI_MAP',
        'OBJECTS',
        'RPM_USER_GROUP',
        'USERS',
        'CME_DOC_STATUS',
        'CME_CUSTODIAN',
        'CME_DOC_TYPE',
        'CME_DEPARTMENT',
        'CME_OWNER',
        'USER_GROUP_USER_XREF'
    )
ORDER BY atc.table_name, atc.column_name;
