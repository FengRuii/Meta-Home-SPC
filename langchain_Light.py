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
url_wiz = "http://homeassistant.local:8123/api/services/light/turn_on"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIzOTU1ZjA0ZTllYmY0NzkxYTdjNjdkMWViMWVhN2QwOSIsImlhdCI6MTcyMjc2Mzk1OSwiZXhwIjoyMDM4MTIzOTU5fQ.wGWQJYfsSdjxdsmU5hLL5t68xsaP0MuQtaB-MFL3A-s"
entity_id_wiz = "light.wiz_rgbw_tunable_4b588c"

#os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ["LANGCHAIN_PROJECT"] = "L3 Research Agent"

# Defining LLM
local_llm = 'llama3'
llama3 = ChatOllama(model=local_llm, temperature=0)
llama3_json = ChatOllama(model=local_llm, format='json', temperature=0)

light_wizard_prompt = PromptTemplate(
    template="""
    
    <|begin_of_text|>
    
    <|start_header_id|>system<|end_header_id|>
    
    You are an expert at understanding a user statement to match the right color hue of the lighting conditions in the room. When the 
    user is talking about a specific event that is going to happen, or a desire to set the mood of the room, you can effectively determine
    which effect to provide to the user.  The available effects are: Ocean, "Romance", "Sunset", "Party", "Fireplace", "Cozy", "Forest", "Pastel Colors",
    "Wake up", "Bedtime", "Warm White", "Daylight", "Cool white", "Night light", "Focus", "Relax", "True colors", "TV time", "Plantgrowth", "Spring",
    "Summer", "Fall", "Deepdive", "Jungle", "Mojito", "Club", "Christmas", "Halloween", "Candlelight", "Golden white", "Pulse", "Steampunk", and "Rhythm". 
    The options are those exactly and you may not modify the words themselves. Give out your best judgement on the theme based on the user statement. 
    Return the JSON always first with a key "entity_id" and a persistent value of "light.wiz_rgbw_tunable_4b588c", and secondly a key
    "effect" with a value that you have determined to be the theme.  You shall return with no preamble or explanation. 

    
    Question to route: {question} 
    
    <|eot_id|>
    
    <|start_header_id|>assistant<|end_header_id|>
    
    """,
    input_variables=["question"],
)

#data_wiz = {
#    "entity_id": entity_id_wiz,
#    "effect": "Romance"  # Replace with your desired RGB color values
#}

# Chain
question_router = light_wizard_prompt | llama3_json | JsonOutputParser()

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
