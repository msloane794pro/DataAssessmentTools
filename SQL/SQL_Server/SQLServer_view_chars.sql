SELECT 
  [ViewName] = v.[name],
  [ColumnName] = c.[name],
  [SourceDataType] = 
    CASE 
      WHEN tp.[name] IN ('varchar', 'char', 'varbinary', 'geometry') THEN tp.[name] + '(' + IIF(c.max_length = -1, 'max', CAST(c.max_length AS VARCHAR(25))) + ')' 
      WHEN tp.[name] IN ('nvarchar', 'nchar') THEN tp.[name] + '(' + IIF(c.max_length = -1, 'max', CAST(c.max_length / 2 AS VARCHAR(25))) + ')'      
      WHEN tp.[name] IN ('decimal', 'numeric') THEN tp.[name] + '(' + CAST(c.[precision] AS VARCHAR(25)) + ', ' + CAST(c.[scale] AS VARCHAR(25)) + ')'
      WHEN tp.[name] IN ('datetime2') THEN tp.[name] + '(' + CAST(c.[scale] AS VARCHAR(25)) + ')'
      ELSE tp.[name]
    END,
  [DataType] = tp.[name],
  [Length] = CASE 
               WHEN tp.[name] IN ('varchar', 'char', 'varbinary', 'geometry') THEN IIF(c.max_length = -1, 'max', CAST(c.max_length AS VARCHAR(25))) 
               WHEN tp.[name] IN ('nvarchar', 'nchar') THEN IIF(c.max_length = -1, 'max', CAST(c.max_length / 2 AS VARCHAR(25)))   
               WHEN tp.[name] IN ('decimal', 'numeric') THEN CAST(c.[precision] AS VARCHAR(25)) + ', ' + CAST(c.[scale] AS VARCHAR(25))
               WHEN tp.[name] IN ('datetime2') THEN CAST(c.[scale] AS VARCHAR(25))
             END
  
FROM sys.views v
JOIN sys.schemas s ON v.schema_id = s.schema_id
JOIN sys.columns c ON v.object_id = c.object_id
JOIN sys.types tp ON c.user_type_id = tp.user_type_id
LEFT JOIN sys.index_columns ic ON ic.object_id = c.object_id AND ic.column_id = c.column_id

-- List views here if the analysis is to be restricted to only certain views.
/*
WHERE v.[name] in (
	'View1',
	'View2',
	'View3'
)
*/

ORDER BY [ViewName], [ColumnName];
