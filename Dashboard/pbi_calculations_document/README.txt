Procedure to create a document showing calculations used by a specific Power BI Dashboard:	
1. Download the Semantic Model from the Power BI Service.	https://app.powerbigov.us/groups/d5c88659-e5d8-4a72-801b-9056521292d3/list
2. Open the Semantic Model in Tabular Editor	
3. Under "Tables" in the TOM Explorer, highlight all the Calculations that you intend to document.	
4. R-Click and select Copy.	
5. Paste the copied content into a JSON file (calculation_groups.json).	
6. A specialized Python Script was developed to parse the JSON Calculation data into Excel.  Download the Python code from GitHub.	https://github.com/msloane794pro/DataAssessmentTools/tree/main/Dashboard/pbi_calculations_document
7a. Update the script if necessary to reflect the desired input and output files.	
7b. Run the Python Script, which creates the initial version of this Excel file.	
8. Cleanup and format the Calculations tab as desired/needed.  You may need to "trim" trailing whitespace from values in the Formula column.	
9. Create values for the Descriptions column using AiVA and the prompt provided.  	
10. Paste the values from the Formula column at the end of the AiVA prompt and send the prompt to AiVA.	https://aiva-ac.inl.gov/
11. Copy the response from AiVA into a TSV file (Text file with tab seperated values).	
12. Due to bandwidth and data limitations, multiple requests to AiVA with smaller data sets may be necessary.	
13. Import the TSV data into Excel into a  "AiVA Simple Descriptions" tab.  (Data --> Get Data --> From File --> From Text/CSV)	
14. Cleanup the Descriptions values as needed.	
15. Use Xlookup to bring in Descriptions from the "AiVA Simple Descriptions" tab into the "Calculations" tab in a new column named "Description (Lookup)".	
16. Verify all Description values are looked up correctly.	
16. Copy only the values from the "Description (Lookup)" column to the "Description" column.	
17. Hide the "Description (Lookup)" column.	
18. Review and edit the Descriptions as needed.	
19. When the document is stable, rename it to include YYYYMMDD as part of the filename.	
20. If major corrections or updates need to be made, create/copy-to a new file file with a new date code in the filename.	
