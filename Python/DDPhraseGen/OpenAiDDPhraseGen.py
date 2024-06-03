# OpenAiDDPhraseGen
# Python class to make Open AI API calls to generate database element descriptions and friendly names.
# Python strings and lists are provided as input to this class and lists are returned as output.
# Copyright 2024 - Michael Sloane - Agree Technologies

# Import needed libraries
import sys
import configparser
from openai import OpenAI
import uuid
from enum import Enum
import os
import datetime
import re

# Define operational constants.
dateLastUpdated = '2024.05.20 03:26:34'
# ai_model_base_url='https://api.hpc.inl.gov/llm/v1'
# ai_model_api_key='5mdim-8qu4h-pq2g7-ivhl6-memyi'
selected_ai_model = 0
tableNameSubstPattern = '~~~tableName~~~'
sessionIdSubstPattern = '~~~sessionId~~~'

class PhraseType(Enum):
    DESCRIPTION = 1
    FRIENDLYNAME = 2



class OpenAiDDPhraseGen:

    _initFile = "properties.txt"
    _initialized = False
    _modelName = ""
    _sessionId = ""
    _sessionGuid = None
    _systemRoleContent = """You are a technical assistant, skilled in explaining complex programming concepts with everyday language."""

    _initialPromtIntro = f"""This is the first prompt of new session of prompts.  
All prompts within this session are to be associated together by a common Session ID.
The Session ID value for this session is: {sessionIdSubstPattern}
Successive prompts will follow this initial prompt and will reference this Session ID value.
The format of the responses for all of the prompts in this session must be consistent with each other.
"""
    
    _successivePromtIntro = f"""This is a successive prompt for a session already in progress.
The Session ID value for this session is: {sessionIdSubstPattern}
The format of the response for this prompt must be consistent with the responses from earlier prompts in this session.
"""

#     _descriptionPrompt = f"""I will provide you with a list of names of data elements within a database table named `{tableNameSubstPattern}`.
# For each of the element names provided in the list, generate a sentence describing the element.
# Return a list of sentence descriptions that correspond to the list of data elements provided.
# Each sentence description should be returned on a single line of text.  
# Always return one sentence for each element name provided, even if there are similarly named elements in the provided list.
# Never mention multiple elements within a single sentance.
# For example, never provide a sentence like `D1 to D9: Nine variables used to store different values or data points within a program.`
# Only return the list of sentence descriptions, and do not return any introductory text.
# For example, do not return a line of text that says `Here is the list of sentence descriptions for table {tableNameSubstPattern}.`
# Here are the list of data element names:
# """

#     _descriptionPrompt = f"""I will provide you with a data table that includes properties of a database table named `{tableNameSubstPattern}`.
# Each row of the data table will consist of an element name and a human readable `Friendly Name` for an element in the database table `{tableNameSubstPattern}`.
# For each row of data, use the element name and the friendly name to generate a sentence describing the element.
# Return each of the sentence descriptions on seperate lines of text.
# Here is the data table:
# """
    
#     _descriptionPromptHTML = f"""Given the following data table containing information from a Drawings Database, produce a description for each entry.
# Return your response as a table of data in HTML table format with the same number of rows as the provided data table.  
# The returned table must have the following columns: 'TableName', 'ColumnName', 'Friendly Name', 'Description' where the 'Description' column contains the description of the entry.
# """

#     _descriptionPromptPandas = f"""Given an input data table containing information from a Drawings Database, produce a description for each entry.
# Return your response as a table of data with the same number of rows as the provided data table.  
# Return the table in the following format used by Python Pandas:  {'TableName': ['table name 1', 'table name 2', 'table name 3'],'ColumnName': ['column name 1', 'column name 2', 'column name 3'],'Friendly Name': ['friendly name 1', 'friendly name 2', 'friendly name 3'],'Description': ['description 1', 'description 2', 'description 3']}
# The returned table must have the following columns: 'TableName', 'ColumnName', 'Friendly Name', 'Description' where the 'Description' column contains the description of the entry.
# Here is the input data table:
# """

    _descriptionPrompt = f"""Given the following data table containing information from a Drawings Database, produce a description for each entry.
Return your response as a table of data in Standardized CSV format.
"Header 1","Header 2","Header 3"
"Value 1","Value 2","Value 3"
"Value 4","Value 5","Value 6"
Only return the CSV data.
Do not include any other text in your response.
The returned table must have the following columns: "TableName", "ColumnName", "Friendly Name", "Description" where the 'Description' column contains the description of the entry.
The number of data value rows returned must exactly equal the number of data rows in the provided data table.
"""



    _friendlyNamesPrompt = f"""I will provide you with a list of names of data elements within a database table named `{tableNameSubstPattern}`. 
For each data element name, I need you to create a `Friendly Name` as follows:
The friendly name for each data element name is to be a human readable set of one or more words, derived from the data element name.
Each friendly name returned should have the first letter of each word in upper case and all other characters in lower case.
Search through the text of each element name and break it up into one or more words seperated by spaces.
Any substring within the element name that matches an English word should be considered one of the seperated words.
If an element name contains a substring that matches a well known English abbreivation, the full text of the abbreviated item should be considered one of the seperated words.
For example the element name HORSEDR should result in the following: Horse Doctor
Interpret the use of camel case or Pascal case within the element name as defining a word boundary.
Interpret the `_` character within a data element name as defining a word boundary.
For example ApprRequestForm_ID would be separated into the following words: Appr Request Form ID
Another example is Escort_ID would be separated into the following words: Escort ID
Another example is LOGEndDate would be separated into the following words: Log End Date
If the data element name consists of a single word, return that word only.
For example a data element name of "BUILDING" would result in the following: Building
Do not include the underscore character `_` in your response.
Do not include an escaped underscore character such as `\_` in your response.
In your response, return exactly one line of words for each data element name.
In your response, each friendly name must be on a seperate line of text.
For example, if the list of data element names provided has 12 data elements listed, your response must contain exactly 12 lines of text.
Do not include any punctuation or numbering in your response.
Do not include the original element name in your response.
Only return the list of friendly names, and do not return any introductory text.
Here are the list of data element names:
"""



    def __init__(self):       
        self.base_url, self.api_key = self.initProperties()
       
        print(f'Initializing OpenAI Client: Base URL: {self.base_url}, API Key: {self.api_key}')
        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        model_list = self._client.models.list()
        model_names = [x.id for x in model_list.data]
        print(f'Model Names available to select: {model_names}')
        self._modelName = model_names[selected_ai_model]


    def initProperties(self):
        try:
            config = configparser.ConfigParser()
            config.read('properties.ini')
            ai_model_base_url = config.get('Properties', 'AI_MODEL_BASE_URL')
            ai_model_api_key = config.get('Properties', 'AI_MODEL_API_KEY')

            # Validate that the API key read is in the expected format.
            pattern = re.compile(r'^[0-9a-z]{5}-[0-9a-z]{5}-[0-9a-z]{5}-[0-9a-z]{5}-[0-9a-z]{5}$', re.IGNORECASE)
            if not bool(pattern.match(ai_model_api_key)):
                print(f'Invalid API Key: {ai_model_api_key}')
                sys.exit()

            return ai_model_base_url, ai_model_api_key
        except:
            print(f"""Properties file error.
A properties file must be created in this directory to allow proper configuration of this application.
Required file name: properties.ini
Required file format:
[Properties]
AI_MODEL_BASE_URL=Insert your OpenAi Base URL here
AI_MODEL_API_KEY=Insert your API key here
""")
            sys.exit()


    def setModel(self, model):
        model_list = self._client.models.list()
        model_names = [x.id for x in model_list.data]
        #print(f'Model Names available to select: {model_names}')
        if model >= len(model_names):
            print(f'Can not set requested model value: {model}')
        else:
            self._modelName = model_names[model]

    def getModelNames(self):
        model_list = self._client.models.list()
        model_names = [x.id for x in model_list.data]
        return model_names

    def greet(self):
        print(f"This is the OpenAiDDPhraseGen class accessing AI Chat at:  {self.base_url}. AI Model = {self._modelName}")

    def getSystemMessage(self):
        message = {"role": "system", "content": self._systemRoleContent}
        return message

    def constructUserMessage(self, content):
            #print(content)
            message = {"role": "user", "content": content}
            return message

    def _chat_completion_request(self, messages, sessionId = "", tools=None, tool_choice=None, ):
        #print(f'messages = {messages}')
        try:
            response = self._client.chat.completions.create(
                model=self._modelName,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
            )

            return response
        except Exception as e:
            print("EXCEPTION: Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            self.log_transcript_message(sessionId, f"Exception: {e}")
            raise SystemError(e)


    def sendSessionPrompt(self, sessionId, sessionType, tableName, elementList):
        userMessageText = self.createSessionMessageText(sessionId, sessionType, tableName, elementList)
        messages = [self.getSystemMessage(), self.constructUserMessage(userMessageText)]
        response = self._chat_completion_request(messages, sessionId)
        responseText = response.choices[0].message.content       
        self.log_transcript_message(sessionId, f'Response received from {self._modelName}:\n{responseText}\n')
        return responseText


    def createSessionMessageText(self, sessionId, sessionType, tableName, elementList):
        introText = self.manageSession(sessionId)

        #print(f'Element list: {elementList}')

        #Convert list to string with seperate lines for each item in list
        elementListString = "\n".join(str(x) for x in elementList)

        if sessionType == PhraseType.DESCRIPTION.name:
            promptString = self._descriptionPrompt.replace(tableNameSubstPattern, tableName)
        else:
            promptString = self._friendlyNamesPrompt.replace(tableNameSubstPattern, tableName)

        promptContent = introText + promptString + elementListString
        self.log_transcript_message(sessionId, promptContent)

        return (promptContent)


    def manageSession(self, sessionId):
        if sessionId != '':
            if sessionId != self._sessionId:
                self.log_transcript_message(sessionId, f'Session Transcript {sessionId} - AI Model: {self._modelName}')
                self._sessionId = sessionId
                self._sessionGuid = uuid.uuid4()
                introText = self._initialPromtIntro.replace(sessionIdSubstPattern, str(self._sessionGuid))
            else:
                introText = self._successivePromtIntro.replace(sessionIdSubstPattern, str(self._sessionGuid))
        else:
            introText = ''
            self._sessionGuid = None
        return introText
    

    def log_transcript_message(self, transcript_id, message):
        # Define the file name
        file_name = f"{transcript_id}_transcript.txt"

        # Check if the file exists, if not create it
        if not os.path.isfile(file_name):
            with open(file_name, 'w') as f:
                pass

        # Get the current timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d:%H%M%S.%f")

        # Concatenate the timestamp and the message
        log_entry = f"{timestamp} : {message}"

        # Append the log entry to the file
        with open(file_name, 'a') as f:
            f.write(f"{log_entry}\n\n")

