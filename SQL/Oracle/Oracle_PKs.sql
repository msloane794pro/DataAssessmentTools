SELECT
    ac.owner AS "SchemaName",
    ac.table_name AS "TableName",
    acc.column_name AS "ColumnName",
    ac.constraint_name AS "PK_name",
    acc.position AS "ORDINAL_POSITION"
FROM
    all_constraints ac
INNER JOIN
    all_cons_columns acc
ON
    ac.constraint_name = acc.constraint_name
AND
    ac.owner = acc.owner
WHERE
    ac.constraint_type = 'P'
AND
    ac.owner = 'DRAWING'
AND
    ac.table_name IN (
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
    acc.position;
