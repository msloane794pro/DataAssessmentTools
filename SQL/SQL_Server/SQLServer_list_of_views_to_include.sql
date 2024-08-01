SELECT 
    v.name AS ViewName,
    (SELECT COUNT(*) FROM sys.columns AS c WHERE c.object_id = v.object_id) AS NumberOfColumns,
	1 AS Include
FROM 
    sys.views AS v
WHERE 
    v.type = 'V'
    AND v.name NOT LIKE 'dt%' 
ORDER BY 
    v.name;
