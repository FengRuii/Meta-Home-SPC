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

#os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ["LANGCHAIN_PROJECT"] = "L3 Research Agent"

# Defining LLM
local_llm = 'llama3'
llama3 = ChatOllama(model=local_llm, temperature=0)
llama3_json = ChatOllama(model=local_llm, format='json', temperature=0)

stage_prompt = PromptTemplate(
    template="""
    
    <|begin_of_text|>
    
    <|start_header_id|>system<|end_header_id|>
    
    You are an expert at determining either it's conversation stage or action stage. 
    If the user sounds like only trying to have a conversation with you, go directly to "conversation"
    Otherwise, if there are possible actions to take based on the user input, such as an opportunity to change ambient light, which is defined as an upcoming event, or an direct request, or change temperature of the room, go to "action". 
    Within action, use best judgement to determine if the user's request is binary mood related or temperature related.  Return "temp" only when the user express hot or cold, or explicitly mention the climate or current tempearture. Otherwise, return mood.

    
    Return the JSON with one key 'choice' with values of either "conversation" or "action". Another key "pick" with the choice between "mood" or "temp".  Return with no premable or explanation. 

    Question to route: {question} 
    
    <|eot_id|>
    
    <|start_header_id|>assistant<|end_header_id|>
    
    """,
    input_variables=["question"],
)

# Chain
question_router = stage_prompt | llama3_json | JsonOutputParser()

# Test Run
question = input("say something:")
print(question_router.invoke({"question": question}))

