SELECT 
    at.table_name AS "TableName",
    COUNT(ac.column_name) AS "NumberOfColumns",
    at.num_rows AS "NumberOfRows",
    CASE 
        WHEN at.num_rows > 0 THEN '1'
        ELSE '0'
    END AS "Include"
FROM 
    all_tab_columns ac
JOIN 
    all_tables at
ON 
    ac.table_name = at.table_name 
    AND ac.owner = at.owner
WHERE 
    at.owner = 'TRAIN' -- Edit Schema name as needed.
    AND at.num_rows IS NOT NULL
GROUP BY 
    at.table_name,
    at.num_rows
ORDER BY 
    "Include" DESC,
    at.table_name;
