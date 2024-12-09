SELECT 
    *
FROM 
    all_tables at
WHERE 
    at.owner = 'CONCUR'
ORDER BY 
    at.table_name;    