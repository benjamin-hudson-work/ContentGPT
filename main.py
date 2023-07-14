import streamlit as st
import pinecone
import json
import openai
import os
import pandas as pd
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

with open('OpenAI API Key.txt') as f: #Temp
    contents = f.read()
openai.api_key = contents  #st.secrets[openAiKey] #only works on deployment
with open('Pinecone API Key.txt') as f: #Temp
    contents = f.read()
pinecone.api_key = contents  #st.secrets[openAiKey] #only works on deployment
MODEL = "gpt-3.5-turbo"

##res = openai.Embedding.create(
##    input=[
##        "Sample document text goes here",
##        "there will be several phrases in each batch"
##    ], engine=MODEL
##)
##
##pinecone.init(
##    api_key="YOUR_API_KEY",
##    environment="asia-southeast1-gcp-free" 
##)
### check if 'openai' index already exists (only create index if not)
##if 'openai' not in pinecone.list_indexes():
##    pinecone.create_index('conversion', dimension=len(embeds[0]))
### connect to index
##index = pinecone.Index('conversion')

#Get the AI into character
messages = [{"role": "system", "content": "You are an intelligent assistant. Your focus is on conversion marketing. Answer the question as truthfully as possible."} ]

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

start = st.button("Start!")
if start: #Execute code here
    if url:
        path = urlparse(url).path #Shorten link to ease AI's understanding
        messages.append( 
            {"role": "user", "content": "Tell me what the name of the product on this page is: " + path + " Then, tell me what would you change the name of the previous product to in order to improve conversion?"},
        )
        chat = openai.ChatCompletion.create(
            model=MODEL, messages=messages
        )
        reply = chat.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        messages