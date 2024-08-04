import speech_recognition as sr
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_community.chat_models import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langgraph.graph import END, StateGraph
# For State Graph 
from typing_extensions import TypedDict
import os
import requests
import subprocess

#HA Setup
HOME_ASSISTANT_URL = 'http://homeassistant.local:8123/'
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIzOTU1ZjA0ZTllYmY0NzkxYTdjNjdkMWViMWVhN2QwOSIsImlhdCI6MTcyMjc2Mzk1OSwiZXhwIjoyMDM4MTIzOTU5fQ.wGWQJYfsSdjxdsmU5hLL5t68xsaP0MuQtaB-MFL3A-s'

#HA URLs:
url_light = "http://homeassistant.local:8123/api/services/light/turn_on"
url_temp = "http://homeassistant.local:8123/api/services/climate/set_temperature"

# Set the HA headers and payload
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

#Keyword Setup
recognizer = sr.Recognizer()
keywords = ["meta","metta", "Meadow", "llama", "lama"]

#langchain Setup
#os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ["LANGCHAIN_PROJECT"] = "L3 Research Agent"
local_llm = 'llama3'
llama3 = ChatOllama(model=local_llm, temperature=0)
llama3_json = ChatOllama(model=local_llm, format='json', temperature=0)

#Conversation Stage Wizard
stage_prompt = PromptTemplate(
    template="""
    
    <|begin_of_text|>
    
    <|start_header_id|>system<|end_header_id|>
    
    You are an expert at determining either it's conversation stage or action stage. 
    For instance, "how are you doing?" is a conversation.  "Who are you?" is also a conversation starter.  
    Questions about you are conversations. For instance, "What makes you unique?" is a conversation. 
    Questions like "Who made you?" are also conversations. 
    Otherwise, if there are possible actions to take based on the user input, such as an opportunity to change ambient light, which is defined as an upcoming event, or an direct request, or change temperature of the room, go to "action". 
    Within action, use best judgement to determine if the user's request is binary mood related or temperature related.  Return "temp" only when the user express hot or cold, or explicitly mention the climate or current tempearture. Otherwise, return mood.


    
    Return the JSON with one key 'choice' with values of either "conversation" or "action". Another key "pick" with the choice between "mood" or "temp".  Return with no premable or explanation. 

    Question to route: {question} 
    
    <|eot_id|>
    
    <|start_header_id|>assistant<|end_header_id|>
    
    """,
    input_variables=["question"],
)
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
# Temperature Wizard
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

chat_prompt = PromptTemplate(
    template="""
    
    <|begin_of_text|>
    
    <|start_header_id|>system<|end_header_id|> 
    
    You are an smart home AI assistant that is witty and friendly.  Answer in a concise sentence. No apostrophes in sentence.  For instance, replace I'm with "I am" to avoid apostrophes, and "what is" instead of "what's".  
    
    <|eot_id|>
    
    <|start_header_id|>user<|end_header_id|>
    
    Question: {question} 
    
    <|eot_id|>
    
    <|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["question"],
)

light_reply_prompt = PromptTemplate(
    template="""
    
    <|begin_of_text|>
    
    <|start_header_id|>system<|end_header_id|> 
    
    Give a friendly comment on what the user requested, mention that it is fufilled and that you have chosen one of these effects for light: 
    The available effects are: Ocean, "Romance", "Sunset", "Party", "Fireplace", "Cozy", "Forest", "Pastel Colors",
    "Wake up", "Bedtime", "Warm White", "Daylight", "Cool white", "Night light", "Focus", "Relax", "True colors", "TV time", "Plantgrowth", "Spring",
    "Summer", "Fall", "Deepdive", "Jungle", "Mojito", "Club", "Christmas", "Halloween", "Candlelight", "Golden white", "Pulse", "Steampunk", and "Rhythm".
    Give a reason for your choice.  Be friendly and concise.  All in one sentence.  No apostrophes in sentence. For instance, replace I'm with "I am" to avoid apostrophes, and "what is" instead of "what's".
    
    <|eot_id|>
    
    <|start_header_id|>user<|end_header_id|>
    
    Question: {question} 
    
    <|eot_id|>
    
    <|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["question"],
)

temp_reply_prompt = PromptTemplate(
    template="""
    
    <|begin_of_text|>
    
    <|start_header_id|>system<|end_header_id|> 
    
    Briefly mention that you have adjusted the temperature accordingly based on the user request, be friendly and reassuring. In one sentence. No apostrophes in sentence. For instance, replace I'm with "I am" to avoid apostrophes, and "what is" instead of "what's".
    
    <|eot_id|>
    
    <|start_header_id|>user<|end_header_id|>
    
    Question: {question} 
    
    <|eot_id|>
    
    <|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["question"],
)


stage_router = stage_prompt | llama3_json | JsonOutputParser()
light_router = light_wizard_prompt | llama3_json | JsonOutputParser()
temp_router = temp_wizard_prompt | llama3_json | JsonOutputParser()
chat = chat_prompt | llama3 | StrOutputParser()
lightComment = light_reply_prompt | llama3 | StrOutputParser()
tempComment = temp_reply_prompt | llama3 | StrOutputParser()


def changeLight(input):
    light_json = (light_router.invoke({"question": input}))
    response = requests.post(url_light, headers=headers, json=light_json)
    print(light_json)
    print(response)
    if response.status_code == 200:
        print("Success: The light color has been changed.")
        reply = lightComment.invoke({"question": input})
        print(reply)
        #os.system(f"say {reply}")
        subprocess.call(["say",reply])
    else:
        print(f"Failed: {response.status_code} - {response.text}")
        os.system(f'say sorry, something went wrong with the lightbulb')
        

def changeTemp(input):
    temp_json = (temp_router.invoke({"question": input}))
    response = requests.post(url_temp, headers=headers, json=temp_json)
    print(temp_json)
    print(response)
    if response.status_code == 200:
        print("Success: The thermostat temperature has been changed.")
        reply = tempComment.invoke({"question": input})
        print(reply)
        #os.system(f"say {reply}")
        subprocess.call(["say",reply])
    else:
        print(f"Failed: {response.status_code} - {response.text}")
        os.system(f'say sorry, something went wrong with the thermostat')

def route_question(input):
    questionCheck = stage_router.invoke({"question": input})
    if questionCheck['choice'] == "conversation":
        print("Conversation")
        reply = chat.invoke({"question": input})
        print(reply)
        #os.system(f"say {reply}")
        subprocess.call(["say",reply])
    elif questionCheck['choice'] == "action":
        if questionCheck['pick'] == "mood":
            print("Change light")
            changeLight(input)
        if questionCheck['pick'] == "temp":
            print("Change temperature")
            changeTemp(input)
        
#while True:
#    userInput = input("Say something: ")
#    route_question(userInput)

def listen_for_keywords():
    with sr.Microphone() as source:
        print("Listening for keywords...")
        while True:
            try:
                # Adjust for ambient noise and record audio
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

                # Recognize the speech
                speech_text = recognizer.recognize_google(audio)
                print(f"Recognized speech: {speech_text}")

                # Check if any keyword is in the recognized speech
                for keyword in keywords:
                    if keyword in speech_text.lower():
                        question = extract_question(speech_text.lower(), keyword)
                        print(f"Keyword '{keyword}' detected. Recorded question: {question}")
                        route_question(question)
                        break

            except sr.UnknownValueError:
                print("Could not understand the audio")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")

def extract_question(speech_text, keyword):
    # Extract the part of the speech text that comes after the keyword
    return speech_text.split(keyword, 1)[1].strip()

if __name__ == "__main__":
    listen_for_keywords()

