SELECT 
  t.[name] AS [TableName],
  c.[name] AS [ColumnName],
  CASE 
    WHEN tp.[name] IN ('varchar', 'char', 'varbinary', 'geometry') THEN tp.[name] + '(' + IIF(c.max_length = -1, 'max', CAST(c.max_length AS VARCHAR(25))) + ')' 
    WHEN tp.[name] IN ('nvarchar','nchar') THEN tp.[name] + '(' + IIF(c.max_length = -1, 'max', CAST(c.max_length / 2 AS VARCHAR(25)))+ ')'      
    WHEN tp.[name] IN ('decimal', 'numeric') THEN tp.[name] + '(' + CAST(c.[precision] AS VARCHAR(25)) + ', ' + CAST(c.[scale] AS VARCHAR(25)) + ')'
    WHEN tp.[name] IN ('datetime2') THEN tp.[name] + '(' + CAST(c.[scale] AS VARCHAR(25)) + ')'
    ELSE tp.[name]
  END AS [SourceDataType],
  tp.[name] AS [DataType],
  [Length]    =  CASE 
					WHEN tp.[name] IN ('varchar', 'char', 'varbinary', 'geometry') THEN   IIF(c.max_length = -1, 'max', CAST(c.max_length AS VARCHAR(25))) 
					WHEN tp.[name] IN ('nvarchar','nchar') THEN   IIF(c.max_length = -1, 'max', CAST(c.max_length / 2 AS VARCHAR(25)))   
					WHEN tp.[name] IN ('decimal', 'numeric') THEN  CAST(c.[precision] AS VARCHAR(25)) + ', ' + CAST(c.[scale] AS VARCHAR(25)) 
					WHEN tp.[name] IN ('datetime2') THEN   CAST(c.[scale] AS VARCHAR(25)) 
                  END,
  IsPrimaryKeyQuery.IsPrimaryKey,
  CASE 
    WHEN IsPrimaryKeyQuery.IsPrimaryKey = 1 THEN kcu.CONSTRAINT_NAME
    ELSE NULL
  END AS [PK_Name],
  CASE 
    WHEN IsPrimaryKeyQuery.IsPrimaryKey = 1 AND pkcc.Column_Count > 1 THEN CAST(1 AS BIT)
    WHEN IsPrimaryKeyQuery.IsPrimaryKey = 1 AND pkcc.Column_Count = 1 THEN CAST(0 AS BIT)
    ELSE NULL
  END AS [IsCompositePK],
  CASE 
    WHEN IsPrimaryKeyQuery.IsPrimaryKey = 1 THEN kcu.ORDINAL_POSITION
    ELSE NULL
  END AS [PK_Ordinal_position]

FROM sys.tables t
JOIN sys.schemas s ON t.schema_id = s.schema_id
JOIN sys.columns c ON t.object_id = c.object_id
JOIN sys.types tp ON c.user_type_id = tp.user_type_id
LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS kcu 
  ON t.[name] = kcu.TABLE_NAME 
  AND s.[name] = kcu.TABLE_SCHEMA 
  AND c.[name] = kcu.COLUMN_NAME 
LEFT JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS tc 
  ON kcu.CONSTRAINT_SCHEMA = tc.CONSTRAINT_SCHEMA 
  AND kcu.TABLE_NAME = tc.TABLE_NAME 
  AND kcu.CONSTRAINT_NAME = tc.CONSTRAINT_NAME 
  AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
OUTER APPLY (
    SELECT COUNT(*) AS Column_Count
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS kcu2
    WHERE kcu2.TABLE_NAME = kcu.TABLE_NAME 
      AND kcu2.TABLE_SCHEMA = kcu.TABLE_SCHEMA 
      AND kcu2.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
) AS pkcc
CROSS APPLY (
    SELECT CASE 
             WHEN kcu.CONSTRAINT_NAME IS NOT NULL AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY' THEN CAST(1 AS BIT)
             ELSE CAST(0 AS BIT)
           END AS IsPrimaryKey
) AS IsPrimaryKeyQuery

-- List tables here if the analysis is to be restricted to only certain tables.
/*
WHERE t.[name] in (
	'Table1',
	'Table2',
	'Table3'
)
*/

ORDER BY t.[name], c.[name], kcu.ORDINAL_POSITION, kcu.CONSTRAINT_NAME;
