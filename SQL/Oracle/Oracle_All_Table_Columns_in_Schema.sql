SELECT 
    *
FROM 
    all_tab_columns ac
WHERE 
    ac.owner = 'CONCUR'
ORDER BY 
    ac.table_name;    