SELECT 
    acc.owner AS "SchemaName",
    acc.table_name AS "TableName",
    acc.column_name AS "ColumnName",
    acc.constraint_name AS "PK name",
    acc.position AS "ORDINAL_POSITION"
FROM 
    all_cons_columns acc
WHERE 
    acc.owner = 'DRAWING' 
    AND acc.constraint_name IN (
        SELECT
            ac.constraint_name
        FROM 
            all_constraints ac
        WHERE 
            ac.owner = 'DRAWING' 
            AND ac.constraint_type = 'P'
            AND ac.table_name IN ('A_DRAFTERS', 'A_DRAWINGS', 'ARP_REPORT', 'CLOSED_DARS', 'DRAFTERS', 'DRAW_NUMBERING', 'DRAWINGS', 'DRAWINGS_AUDIT', 'ENGINEERS', 'ERROR_LOG', 'ESSENTIAL_AREA', 'ESSENTIAL_LOG', 'INDEX_CODES', 'MARKUPTAB', 'OLD_CAD', 'SPECIAL_CODES', 'SPECIAL_CODES_LOG', 'STW_DRAWINGS', 'SUPERSEDED_DRAWINGS', 'SYSTEM_CODES', 'SYSTEM_LOV')
    )
ORDER BY 
    acc.table_name,
    acc.position;