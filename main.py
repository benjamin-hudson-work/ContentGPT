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
from urllib.parse import urlencode
MODEL = "gpt-3.5-turbo"
EMODEL = "text-embedding-ada-002"

openai.api_key = st.secrets['OPENAI_KEY'] 
pApiKey = st.secrets['PINECONE_KEY'] 
scrapeopsKey = st.secrets['SCRAPEOPS_KEY']
ac="text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}

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

def scrapeops_url(url):
    payload = {'api_key': scrapeopsKey, 'url': url, 'country': 'us'}
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    return proxy_url

def scrape(url, target): #Inputs are url of Walmart store page and the type of data requested.
    resp = requests.get(scrapeops_url(url))#,headers=headers###) 
    #if("Robot or human" in resp.text):
    #    return("False")
    soup = BeautifulSoup(resp.text,'html.parser')
    if "description" in target:
        nextTag = soup.find("script",{"id":"__NEXT_DATA__"})
        jsonData = json.loads(nextTag.text)
        Detail = jsonData['props']['pageProps']['initialData']['data']['product']['shortDescription']
        try:
            return Detail
        except:
            return None
    if "title" in target:
        try:
            return soup.find("h1",{"itemprop":"name"}).text
        except:
            return None

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

try:
    st.session_state["url"]
except NameError:
    st.session_state["url"] = ""
try:
    st.session_state["goal"]
except NameError:
    st.session_state["goal"] = ""
try:
    st.session_state["start"]
except NameError:
    st.session_state["start"] = False
    
url = st.session_state["url"]
goal = st.session_state["goal"]
if st.session_state["start"]: #Execute code here (TODO: Define function)
    if url:
        path = urlparse(url).path #Shorten link to ease AI's understanding
        if goal == "Optimize Title":
            name = scrape(url, "title")
            compiled_question = "Tell me what the name of the product on this page is: " + name + " Then, tell me what would you change the name of the previous product to in order to improve conversion?"
            ask_AI(compiled_question)
        elif goal == "Optimize Features":
            description = scrape(url, "description")
            compiled_question = "Tell me what the name of the product on this page is: " + path + " Then, tell me how you would change this following product description to improve conversion?" + description
            ask_AI(compiled_question)
        elif goal == "Optimize All Content": 
            name = scrape(url, "title")
            description = scrape(url, "description")
            compiled_question = "Tell me what the name of the product on this page is: " + path + " Then, tell me what would you change the name of the previous product to in order to improve conversion? Then, tell me how you would change this following product description to improve conversion?" + description
            ask_AI(compiled_question)
        else:
            "error"
    st.session_state["start"] = False

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
 
st.session_state["url"] = st.text_input("Item page url")
st.session_state["goal"] = st.radio("Goal: ", ["Optimize Title", "Optimize Features", "Optimize All Content"])
st.session_state["keywords_input"] = st.text_input("Which keywords would you like ChatGPT to emphasize? (Unfinished Feature)")

#Press button to send input
st.session_state["start"] = st.button("Start!")

