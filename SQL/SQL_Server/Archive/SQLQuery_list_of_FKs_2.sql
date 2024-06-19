SELECT
    SchemaName = FK.TABLE_SCHEMA,
    TableName = FK.TABLE_NAME,
    ColumnName = CU.COLUMN_NAME,
    FK_name = C.CONSTRAINT_NAME,
    ReferencedTable = PK.TABLE_NAME,
    ReferencedColumn = PT.COLUMN_NAME
FROM 
    INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS C
INNER JOIN 
    INFORMATION_SCHEMA.TABLE_CONSTRAINTS FK ON C.CONSTRAINT_NAME = FK.CONSTRAINT_NAME
INNER JOIN 
    INFORMATION_SCHEMA.TABLE_CONSTRAINTS PK ON C.UNIQUE_CONSTRAINT_NAME = PK.CONSTRAINT_NAME
INNER JOIN 
    INFORMATION_SCHEMA.KEY_COLUMN_USAGE CU ON C.CONSTRAINT_NAME = CU.CONSTRAINT_NAME
INNER JOIN 
    (SELECT
        i1.TABLE_NAME, i2.COLUMN_NAME
    FROM 
        INFORMATION_SCHEMA.TABLE_CONSTRAINTS i1
    INNER JOIN 
        INFORMATION_SCHEMA.KEY_COLUMN_USAGE i2 ON i1.CONSTRAINT_NAME = i2.CONSTRAINT_NAME
    WHERE 
        i1.CONSTRAINT_TYPE = 'PRIMARY KEY') PT ON PT.TABLE_NAME = PK.TABLE_NAME
WHERE
	CU.COLUMN_NAME = PT.COLUMN_NAME
		AND
    FK.TABLE_NAME IN (
		'bl',
		'dp',
		'em',
		'fl',
		'rm',
		'rmcat',
		'rmtype'
	) AND
	PK.TABLE_NAME IN (
		'bl',
		'dp',
		'em',
		'fl',
		'rm',
		'rmcat',
		'rmtype'
	)
ORDER BY [TableName], [ColumnName];