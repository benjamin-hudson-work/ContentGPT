import streamlit as st
import pinecone
import json
import openai
import os
import pandas as pd
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from streamlit_chat import message
MODEL = "gpt-3.5-turbo"
EMODEL = "text-embedding-ada-002"

openai.api_key = st.secrets['OPENAI_KEY'] 
pApiKey = st.secrets['PINECONE_KEY'] 
ac="text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
headers={"Referer":"https://www.google.com","Connection":"Keep-Alive","Accept-Language":"en-US,en;q=0.9","Accept-Encoding":"gzip, deflate, br","Accept":ac,"User-Agent":"Mozilla/5.0 (iPad; CPU OS 9_3_5 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13G36 Safari/601.1"}

#Pinecone Block#

res = openai.Embedding.create(
    input=[
        "Sample document text goes here",
        "there will be several phrases in each batch"
    ], engine=EMODEL
)

# extract embeddings to a list
embeds = [record['embedding'] for record in res['data']]

pinecone.init(
    api_key=pApiKey,
    environment="asia-southeast1-gcp-free" 
)
# check if 'conversion' index already exists (only create index if not)
if 'conversion' not in pinecone.list_indexes():
    pinecone.create_index('conversion', dimension=len(embeds[0]))
# connect to index
index = pinecone.Index('conversion')

#Webscraping Block#

def scrape(url, target): #Inputs are url of Walmart store page and the type of data requested.
    resp = requests.get(url, headers=headers)
    if("Robot or human" in resp.text):
        return "False"
    soup = BeautifulSoup(resp.text,'html.parser')
    l=[]
    obj={}
    if "description" in target:
        nextTag = soup.find("script",{"id":"__NEXT_DATA__"})
        jsonData = json.loads(nextTag.text)
        Detail = jsonData['props']['pageProps']['initialData']['data']['product']['shortDescription']
        try:
            obj["detail"] = Detail
        except:
            obj["detail"]=None
    if "title" in target:
        try:
            obj["name"] = soup.find("h1",{"itemprop":"name"}).text
        except:
            obj["name"]=None
    l.append(obj)
    return obj

#Ai Code Block#

#Get the AI into character
messages = [{"role": "system", "content": "You are an intelligent assistant. Your focus is on conversion marketing. Answer the question as truthfully as possible."} ]

#Store conversation through refreshes
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

#Function that asks ChatGPT question based on user input
def ask_AI(question):
    messages.append( 
        {"role": "user", "content": question},
    )
    chat = openai.ChatCompletion.create(
        model=MODEL, messages=messages
    )
    reply = chat.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})

    #Store output
    st.session_state.generated.append(reply)
    st.session_state.past.append(question)

#UI Block#

repeat = st.button("Repeat")
if repeat:
    ask_AI(st.session_state["past"][-1])

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        #st.session_state["generated"][i] #For testing
        message(st.session_state["generated"][i],seed=50 , key=str(i)) #only works in deployment
        #message(st.session_state['past'][i], is_user=True,avatar_style="adventurer",seed=49, key=str(i) + '_user') #Display the question asked

st.title("ContentGPT")
#Sidebar content: link to Github
st.sidebar.markdown("[![Click!](./app/static/git.png)](https://github.com/benjamin-hudson-work/ContentGPT)")
st.sidebar.markdown("[![Click!](./app/static/HG.png)](https://harvestgroup.com/)")
st.sidebar.markdown("[![Click!](./app/static/Walmart.png)](https://www.walmart.com/)")

"Welcome! This webapp utilizes ChatGPT to interpret a page for a item on Walmart's website and improve its content for search algorithms!"

"First, input the URL for the item on Walmart's online store, then select which aspect you would like this to improve, then optionally select priority keywords."
 
url = st.text_input("Item page url")
goal = st.radio("Goal: ", ["Optimize Title", "Optimize Features", "Optimize All Content"])
keywords_input = st.text_input("Which keywords would you like ChatGPT to emphasize? (Unfinished Feature)")

#Press button to send input
start = st.button("Start!")
if start: #Execute code here (TODO: Define function)
    if url:
        path = urlparse(url).path #Shorten link to ease AI's understanding
        if goal == "Optimize Title":
            name = scrape(url, "title")
            name
            compiled_question = "Tell me what the name of this product is: " + name.get(0) + " Then, tell me what would you change the name of the previous product to in order to improve conversion?"
            ask_AI(compiled_question)
        elif goal == "Optimize Features":
            description = scrape(url, "description")
            compiled_question = "Tell me what the name of the product on this page is: " + path + " Then, tell me how you would change this following product description to improve conversion?" + description.get(0)
            ask_AI(compiled_question)
        elif goal == "Optimize All Content":
            print("Coming soon")
        else:
            print("error")
