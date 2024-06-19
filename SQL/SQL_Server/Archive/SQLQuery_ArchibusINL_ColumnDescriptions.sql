select TRIM(table_name) as [TableName], TRIM(field_name) as [ColumnName], TRIM(ml_heading) as [Description]
from afm_flds 
order by table_name, field_name