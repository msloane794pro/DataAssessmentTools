SELECT
    a.owner AS "SchemaName",
    a.table_name AS "TableName",
    b.column_name AS "ColumnName",
    a.constraint_name AS "FK_name",
    c_pk.table_name AS "ReferencedTable",
    b_pk.column_name AS "ReferencedColumn"
FROM
    all_constraints a
JOIN
    all_cons_columns b ON a.constraint_name = b.constraint_name AND a.owner = b.owner
JOIN
    all_constraints c_pk ON a.r_constraint_name = c_pk.constraint_name AND a.r_owner = c_pk.owner
JOIN
    all_cons_columns b_pk ON c_pk.constraint_name = b_pk.constraint_name AND c_pk.owner = b_pk.owner AND b.position = b_pk.position
WHERE
    a.constraint_type = 'R'
AND
    a.owner = 'DRAWING'
AND
    a.table_name IN (
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
    "TableName",
    "ColumnName";
