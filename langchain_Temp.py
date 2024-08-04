import requests
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_community.chat_models import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langgraph.graph import END, StateGraph
# For State Graph 
from typing_extensions import TypedDict
import os

# Replace with your Home Assistant instance URL and your access token
HOME_ASSISTANT_URL = 'http://homeassistant.local:8123/'
ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIzOTU1ZjA0ZTllYmY0NzkxYTdjNjdkMWViMWVhN2QwOSIsImlhdCI6MTcyMjc2Mzk1OSwiZXhwIjoyMDM4MTIzOTU5fQ.wGWQJYfsSdjxdsmU5hLL5t68xsaP0MuQtaB-MFL3A-s'

# Define your Home Assistant details
url_wiz = "http://homeassistant.local:8123/api/services/climate/set_temperature"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIzOTU1ZjA0ZTllYmY0NzkxYTdjNjdkMWViMWVhN2QwOSIsImlhdCI6MTcyMjc2Mzk1OSwiZXhwIjoyMDM4MTIzOTU5fQ.wGWQJYfsSdjxdsmU5hLL5t68xsaP0MuQtaB-MFL3A-s"
#entity_id_wiz = "light.wiz_rgbw_tunable_4b588c"

#os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ["LANGCHAIN_PROJECT"] = "L3 Research Agent"

# Defining LLM
local_llm = 'llama3'
llama3 = ChatOllama(model=local_llm, temperature=0)
llama3_json = ChatOllama(model=local_llm, format='json', temperature=0)

temp_wizard_prompt = PromptTemplate(
    template="""
    
    <|begin_of_text|>
    
    <|start_header_id|>system<|end_header_id|>
    
    You are an expert at understanding a user's question, and change the temperature of the room for better comfort. 
    Return the JSON always first with a key "entity_id" and a persistent value of "climate.thermostat", and secondly a key
    "temperature" between 65F to 85F in Fahrenheit based on your judgement of the user's need, do not use just 72 as the best comfort. 
    Third, return a key "hvac_mode" with a value of either "heat", or "cool" based on the user needs, if the user feels warm, return "cool", if the user feels cold, return "heat". You shall return with no preamble or explanation. 
    
    Question to route: {question} 
    
    <|eot_id|>
    
    <|start_header_id|>assistant<|end_header_id|>
    
    """,
    input_variables=["question"],
)

# Set the headers and payload
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

#data_wiz = {
#    "entity_id": entity_id_wiz,
#    "effect": "Romance"  # Replace with your desired RGB color values
#}

# Chain
question_router = temp_wizard_prompt | llama3_json | JsonOutputParser()

# Test Run
question = input("Please enter something: ")
data_wiz = (question_router.invoke({"question": question}))
print(data_wiz)

# Make the POST request to Home Assistant
response_wiz = requests.post(url_wiz, headers=headers, json=data_wiz)
print(response_wiz)

# Check the response
if response_wiz.status_code == 200:
    print("Success: The light color has been changed.")
else:
    print(f"Failed: {response_wiz.status_code} - {response_wiz.text}")
