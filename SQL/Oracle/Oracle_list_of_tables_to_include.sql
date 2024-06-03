SELECT DISTINCT
    t.TABLE_NAME AS "TableName", 
    (SELECT COUNT(*) FROM ALL_TAB_COLUMNS c WHERE c.TABLE_NAME = t.TABLE_NAME) AS "NumberOfColumns",
    NVL(tt.NUM_ROWS, 0) AS "NumberOfRows",
    CASE 
        WHEN NVL(tt.NUM_ROWS, 0) = 0 
        THEN '0' 
        ELSE '1' 
    END AS "Include"
FROM ALL_TAB_COLUMNS t
JOIN DBA_TABLES tt ON t.TABLE_NAME = tt.TABLE_NAME
WHERE t.OWNER = 'DRAWING' 
ORDER BY "Include" desc, t.TABLE_NAME;