SELECT 
    t.name AS TableName,
	(SELECT COUNT(*) FROM sys.columns AS c WHERE c.object_id = t.object_id) AS NumberOfColumns,
    SUM(p.rows) AS NumberOfRows,
    iif( p.rows = 0, 0, 1 ) AS Include
FROM 
    sys.tables AS t
    JOIN sys.partitions AS p ON t.object_id = p.object_id
    JOIN sys.allocation_units AS a ON p.partition_id = a.container_id
WHERE 
    t.type = 'u'
    AND t.name NOT LIKE 'dt%' 
GROUP BY 
    t.name, t.object_id, p.rows
ORDER BY 
    Include desc, t.name;