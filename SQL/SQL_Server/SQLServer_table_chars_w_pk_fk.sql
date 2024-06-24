SELECT 
  [TableName] = t.[name],
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
             END,
  [IsPrimaryKey] = CASE 
                     WHEN ic.column_id IS NOT NULL AND i.is_primary_key = 1 THEN 'True'
                     ELSE 'False' 
                   END,
  [PK_name] = CASE WHEN i.is_primary_key = 1 THEN kc.[name] ELSE '' END,
  [PK_ordinal_position] = CASE WHEN i.is_primary_key = 1 THEN ic.key_ordinal ELSE 0 END,
  [IsForeignKey] = CASE 
                     WHEN fkc.parent_column_id IS NOT NULL THEN 'True'
                     ELSE 'False' 
                   END,
  [FK_name] = CASE WHEN fkc.parent_column_id IS NOT NULL THEN fk.[name] ELSE '' END,
  [FK_referenced_table] = CASE WHEN fkc.parent_column_id IS NOT NULL THEN OBJECT_NAME(fk.referenced_object_id) ELSE '' END,
  [FK_referenced_column] = CASE WHEN fkc.parent_column_id IS NOT NULL THEN COL_NAME(fk.referenced_object_id, fkc.referenced_column_id) ELSE '' END
FROM sys.tables t
JOIN sys.schemas s ON t.schema_id = s.schema_id
JOIN sys.columns c ON t.object_id = c.object_id
JOIN sys.types tp ON c.user_type_id = tp.user_type_id
LEFT JOIN sys.index_columns ic ON ic.object_id = c.object_id AND ic.column_id = c.column_id
LEFT JOIN sys.indexes i ON i.object_id = ic.object_id AND i.index_id = ic.index_id AND i.is_primary_key = 1
LEFT JOIN sys.key_constraints kc ON kc.parent_object_id = t.object_id AND kc.type = 'PK' AND kc.unique_index_id = i.index_id
LEFT JOIN sys.foreign_key_columns fkc ON fkc.parent_object_id = t.object_id AND fkc.parent_column_id = c.column_id
LEFT JOIN sys.foreign_keys fk ON fk.object_id = fkc.constraint_object_id

-- List tables here if the analysis is to be restricted to only certain tables.
-- List tables here if the analysis is to be restricted to only certain tables.
/*
WHERE t.[name] in (
	'Table1',
	'Table2',
	'Table3'
)
*/

ORDER BY [TableName], [ColumnName];
