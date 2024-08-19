SELECT 
    icol.table_name,
    icol.index_name,
    icol.column_name,
    icol.column_position
FROM 
    all_ind_columns icol
WHERE 
    icol.table_owner = 'TRAIN' -- Replace with your schema name
    AND icol.index_name LIKE '%PK%' --Specify special identifier for indexes acting as Primary Key
ORDER BY 
    icol.table_name, 
    icol.index_name, 
    icol.column_position;