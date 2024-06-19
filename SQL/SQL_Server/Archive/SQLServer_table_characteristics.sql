SELECT 
  [TableName] = t.[name]
  ,[ColumnName]  = c.[name]
  ,[SourceDataType]    = 
    CASE 
      WHEN tp.[name] IN ('varchar', 'char', 'varbinary', 'geometry') THEN tp.[name] + '(' + IIF(c.max_length = -1, 'max', CAST(c.max_length AS VARCHAR(25))) + ')' 
      WHEN tp.[name] IN ('nvarchar','nchar') THEN tp.[name] + '(' + IIF(c.max_length = -1, 'max', CAST(c.max_length / 2 AS VARCHAR(25)))+ ')'      
      WHEN tp.[name] IN ('decimal', 'numeric') THEN tp.[name] + '(' + CAST(c.[precision] AS VARCHAR(25)) + ', ' + CAST(c.[scale] AS VARCHAR(25)) + ')'
      WHEN tp.[name] IN ('datetime2') THEN tp.[name] + '(' + CAST(c.[scale] AS VARCHAR(25)) + ')'
      ELSE tp.[name]
    END
 , [DataType] = tp.[name]
 , [Length]    =  CASE 
					WHEN tp.[name] IN ('varchar', 'char', 'varbinary', 'geometry') THEN   IIF(c.max_length = -1, 'max', CAST(c.max_length AS VARCHAR(25))) 
					WHEN tp.[name] IN ('nvarchar','nchar') THEN   IIF(c.max_length = -1, 'max', CAST(c.max_length / 2 AS VARCHAR(25)))   
					WHEN tp.[name] IN ('decimal', 'numeric') THEN  CAST(c.[precision] AS VARCHAR(25)) + ', ' + CAST(c.[scale] AS VARCHAR(25)) 
					WHEN tp.[name] IN ('datetime2') THEN   CAST(c.[scale] AS VARCHAR(25)) 
                  END
FROM sys.tables t
JOIN sys.schemas s ON t.schema_id = s.schema_id
JOIN sys.columns c ON t.object_id = c.object_id
JOIN sys.types tp ON c.user_type_id = tp.user_type_id

-- List tables here if the analysis is to be restricted to only certain tables.
/*
WHERE t.[name] in (
	'Table1',
	'Table2',
	'Table3'
)
*/

ORDER BY TableName, ColumnName