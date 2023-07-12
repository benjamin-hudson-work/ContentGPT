import streamlit as st
import pinecone
import json
import openai
import os
import pandas as pd

with open('OpenAI API Key.txt') as f: #Temp
    contents = f.read()
openai.api_key = contents  #st.secrets[openAiKey] #only works on deployment
messages = [ ]#{"role": "system", "content": "You are a intelligent assistant."} ]

st.title("ContentGPT")
source = st.sidebar.markdown("[![Click!](./app/static/git.png)](https://github.com/benjamin-hudson-work/ContentGPT)")

"Welcome! This webapp utilizes ChatGPT to interpret a page for a item on Walmart's website and improve its content for search algorithms!"

"First, input the URL for the item on Walmart's online store, then select which aspect you would like this to improve, then optionally select priority keywords."
 
url = st.text_input("Item page url")
goal = st.radio("Goal: ", ["Optimize Title", "Optimize Features", "Optimize All Content"])
keywords_input = st.text_input("Which keywords would you like ChatGPT to emphasize? (Unfinished Feature)")

start = st.button("Start!")
if start: #Execute code here
    messages.append(
        {"role": "user", "content": "Hello, ChatGPT!"},
    )
    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )
    reply = chat.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    messages

#phone_number = st.slider("Input phone number for more",max_value=9999999999) 