SELECT atc.table_name as "TableName", 
       atc.column_name as "ColumnName",
       CASE 
           WHEN NVL(atc.data_length, 0) = 0 THEN 'NULL' 
           ELSE atc.data_type || '(' || atc.data_length || ')'
       END as "SourceDataType",
       atc.data_type as "DataType", 
       atc.data_length as "Length",
       CASE 
           WHEN pk_col.column_name IS NOT NULL THEN 'True' 
           ELSE 'False'
       END as "IsPrimaryKey",
       COALESCE(pk_col.constraint_name, '') as "PK_name",
       COALESCE(pk_col.position, 0) as "PK_ordinal_position",
       CASE 
           WHEN fk_info.constraint_name IS NOT NULL THEN 'True' 
           ELSE 'False'
       END as "IsForeignKey",
       COALESCE(fk_info.constraint_name, '') as "FK_name",
       COALESCE(fk_info.r_table_name, '') as "FK_referenced_table",
       COALESCE(fk_info.r_column_name, '') as "FK_referenced_column"
FROM all_tab_columns atc
LEFT JOIN (
    SELECT acc.table_name, acc.column_name, ac.constraint_name, acc.position
    FROM all_cons_columns acc
    JOIN all_constraints ac ON acc.owner = ac.owner AND acc.constraint_name = ac.constraint_name
    WHERE ac.constraint_type = 'P'
      AND ac.owner = 'EDMS70' -- Edit Schema name as needed.
) pk_col ON atc.table_name = pk_col.table_name AND atc.column_name = pk_col.column_name
LEFT JOIN (
    SELECT acc.table_name, acc.column_name, ac.constraint_name, 
           r_ac.table_name AS r_table_name, r_acc.column_name AS r_column_name
    FROM all_cons_columns acc
    JOIN all_constraints ac ON acc.owner = ac.owner AND acc.constraint_name = ac.constraint_name
    JOIN all_constraints r_ac ON ac.r_owner = r_ac.owner AND ac.r_constraint_name = r_ac.constraint_name
    JOIN all_cons_columns r_acc ON r_ac.owner = r_acc.owner AND r_ac.constraint_name = r_acc.constraint_name AND r_acc.position = acc.position
    WHERE ac.constraint_type = 'R'
      AND ac.owner = 'EDMS70' -- Edit Schema name as needed.
) fk_info ON atc.table_name = fk_info.table_name AND atc.column_name = fk_info.column_name
WHERE atc.OWNER = 'EDMS70' -- Edit Schema name as needed.
  -- Un-comment and edit list of tables as needed.
  --AND atc.table_name IN ('DOC_INDEX', 'DRUI', 'DRUI_MAP', 'OBJECTS', 'RPM_USER_GROUP', 'USERS')
ORDER BY atc.table_name, atc.column_name;
