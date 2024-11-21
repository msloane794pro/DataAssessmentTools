SELECT 
    COUNT(DISTINCT TABLE_NAME) AS TotalNumberOfTables,
    COUNT(COLUMN_NAME) AS TotalNumberOfColumns
FROM 
    ALL_TAB_COLUMNS
WHERE 
    OWNER = 'EDMS70' -- Replace with your actual schema name
    AND TABLE_NAME IN 
    (
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
    ) -- Replace with your actual table names