SELECT  Tab.name  as TableName
			 ,'' as SchemaName
			 ,IX.name  as PK_Name			 
			 ,Col.name  ColumnName
			 ,IX.is_primary_key as ORDINAL_POSITION
			 --,IX.type_desc Index_Type
			 --,IXC.is_included_column Is_Included_Column
			 --,IX.fill_factor 
			 --,IX.is_disabled
			 
			 --,IX.is_unique
           FROM  sys.indexes IX 
           INNER JOIN sys.index_columns IXC  ON  IX.object_id   =   IXC.object_id AND  IX.index_id  =  IXC.index_id  
           INNER JOIN sys.columns Col   ON  IX.object_id   =   Col.object_id  AND IXC.column_id  =   Col.column_id     
           INNER JOIN sys.tables Tab      ON  IX.object_id = Tab.object_id
		   where is_unique = 1