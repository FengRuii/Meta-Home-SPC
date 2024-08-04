from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_community.chat_models import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langgraph.graph import END, StateGraph
# For State Graph 
from typing_extensions import TypedDict
import os

#os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ["LANGCHAIN_PROJECT"] = "L3 Research Agent"

# Defining LLM
local_llm = 'llama3'
llama3 = ChatOllama(model=local_llm, temperature=0)
llama3_json = ChatOllama(model=local_llm, format='json', temperature=0)

# Light Wizard

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

# Chain
question_router = light_wizard_prompt | llama3_json | JsonOutputParser()

# Test Run
question = "I'm watching spiderman"
print(question_router.invoke({"question": question}))