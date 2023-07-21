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
        compiled_question = "Tell me what the name of the product on this page is: " + path + " Then, tell me what would you change the name of the previous product to in order to improve conversion?"
        ask_AI(compiled_question)

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state['past'][i], is_user=True,avatar_style="adventurer",seed=49, key=str(i) + '_user')
        message(st.session_state["generated"][i],seed=50 , key=str(i))

repeat = st.button("Repeat")
if repeat:
    ask_AI(st.session_state["past"][-1])