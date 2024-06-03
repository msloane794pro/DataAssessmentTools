import sys
import pandas as pd

def findDescription(df, ind):
    description = ""
    source = "Default"
    try:
        # Search through Column 3 first to see if a description exists.
        # Then look through location in Column 2.
        description = df[3][ind - 1]
        source = "Preferred - [3][ind - 1]"
        if pd.isna(description):
            description = df[3][ind]
            source = "Two - [3][ind]"
            if pd.isna(description):
                description = df[2][ind + 1]
                source = "Three - [2][ind + 1]"
                if pd.isna(description):
                    description = df[2][ind + 2]
                    source = "Four - [2][ind + 2]"
                    if pd.isna(description):
                        description = df[2][ind + 3]
                        source = "Five - [2][ind + 3]"
                        if pd.isna(description):
                            description = ""
                            source = "Not found."
    except:
        # Exceptions may occur, as Column 3 may not exist.
        # Start search on Column 2 only.
        try:
            description = df[2][ind + 1]
            source = "Ex - 1 - [2][ind + 1]"
            if pd.isna(description):
                description = df[2][ind + 2]
                source = "Ex - 2 - [2][ind + 2]"
                if pd.isna(description):
                    description = df[2][ind + 3]
                    source = "Ex - 3 - [2][ind + 3]"
                    if pd.isna(description):
                        description = ""
                        source = "Ex - 3 - Not found"
        except:
            description = ""
            source = "Ex - X - Error state."
    return description,source    


data_from_html = pd.read_html('./PxFieldMapList.html', \
                     skiprows=0)
print("There are {} HTML tables in this HTML file.".format(len(data_from_html)))

col_names = ['TableName', 'ElementName', 'Description', 'SourceLocation']
output_df = pd.DataFrame(columns=col_names)
table_ind = 0
tableNames = []
elementNames = []
descriptions = []
sourceLocations = []




for df in data_from_html: 
    if table_ind < 148:
        #print("Table number {} - Table name: {}, Number of data rows: {}".format(table_ind, df[1][1], df.shape[0]))
        try: 
            elementCount = 0
            for ind in df.index:               
                if df[0][ind] == "PX View":
                    tableName = df[1][ind]
                    elementName = df[1][ind - 1]
                    description, source = findDescription(df, ind)

                    tableNames.append(tableName)
                    elementNames.append(elementName)
                    descriptions.append(description)
                    sourceLocations.append(source)

                    # if description != "":
                    #     print("{} - {} - {}".format(table_ind, ind, description))
                    #     print("          {}".format(source))
                   
        except Exception as e:
            print("Exception caught on table_ind = {}".format(table_ind))
            if hasattr(e, 'message'):
                print("Message: " + e.message)
            else:
                print("Exception: ")
                print(e)
            sys.exit()
   
    

    table_ind = table_ind + 1

print(" {} tableNames were gathered".format(len(tableNames)))
print(" {} elementNames were gathered".format(len(elementNames)))
print(" {} descriptions were gathered".format(len(descriptions)))
print(" {} sourceLocations were gathered".format(len(sourceLocations)))


outputData = {
    'TableName': tableNames, 
    'ElementName': elementNames, 
    'Description': descriptions, 
    'SourceLocation': sourceLocations
}

output_df = pd.DataFrame(outputData)

print(output_df)

output_df.to_excel("output.xlsx", sheet_name='Descriptions', index = False)


