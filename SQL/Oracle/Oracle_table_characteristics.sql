SELECT table_name as "TableName", 
       column_name as "ColumnName",         
       CASE 
           WHEN NVL(data_length, 0) = 0 
           THEN 'NULL' 
           ELSE data_type || '(' || data_length || ')'
       END as "SourceDataType",
       data_type as "DataType", 
       data_length as "Length"
FROM all_tab_columns
WHERE owner = 'DRAWING'  -- Change this value to restrict the list of tables to a specific schema.
    AND table_name in (
        SELECT table_name FROM all_tables
        )
ORDER BY TABLE_NAME;
