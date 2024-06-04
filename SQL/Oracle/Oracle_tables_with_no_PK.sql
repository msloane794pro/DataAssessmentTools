SELECT 
    TABLE_NAME 
FROM 
    ALL_TABLES 
WHERE 
    OWNER = 'DRAWING' -- Replace with schema name
    AND TABLE_NAME NOT IN (
        SELECT 
            TABLE_NAME 
        FROM 
            ALL_CONSTRAINTS 
        WHERE 
            CONSTRAINT_TYPE = 'P' 
            AND OWNER = 'DRAWING' -- Replace with schema name
    )
    AND TABLE_NAME IN (  -- Replace with list of tables
        'A_DRAFTERS',
        'A_DRAWINGS',
        'ARP_REPORT',
        'CLOSED_DARS',
        'DRAFTERS',
        'DRAW_NUMBERING',
        'DRAWINGS',
        'DRAWINGS_AUDIT',
        'ENGINEERS',
        'ERROR_LOG',
        'ESSENTIAL_AREA',
        'ESSENTIAL_LOG',
        'INDEX_CODES',
        'MARKUPTAB',
        'OLD_CAD',
        'SPECIAL_CODES',
        'SPECIAL_CODES_LOG',
        'STW_DRAWINGS',
        'SUPERSEDED_DRAWINGS',
        'SYSTEM_CODES',
        'SYSTEM_LOV'
    )
;