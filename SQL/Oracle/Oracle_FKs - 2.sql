SELECT 
    ac.owner AS SchemaName,
    ac.table_name AS TableName,
    ac.column_name AS ColumnName,
    ac.constraint_name AS ForeignKey_name,
    ac.constraint_name AS ReferencedTable,
    ac.column_name AS ReferencedColumn
FROM 
    all_cons_columns ac,
    all_constraints rc
WHERE 
    ac.owner = 'DRAWING' 
    AND ac.constraint_name = rc.constraint_name
    AND ac.owner = rc.owner
    AND rc.constraint_type = 'R'
    AND ac.table_name IN (
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
ORDER BY 
    ac.table_name,
    ac.position;