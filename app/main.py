import os
import re
import json
import requests

import streamlit as st

from requests.exceptions import ConnectionError


############ DEFINITIONS ############
def start_server():
    os.system("uvicorn inference.server:app --port 8080 --host 0.0.0.0")
    st.session_state['server_started'] = True

def stop_server():
    os.system("kill $(lsof -t -i:8080)")
    st.session_state['server_started'] = False

def check_server():
    try:
        requests.post("http://localhost:8080/warmup")
        return True
    except ConnectionError:
        return False

def restart_server():
    stop_server()
    start_server()

def get_answer(prompt, chat_history):
    payload = {
        "prompt": prompt,
        "chat_history": chat_history
    }
    response = requests.post("http://localhost:8080/", json=payload)
    return response.json()


def parse_response(response: dict) -> str:
    """
    Returns the answer and adds markdown references to the source documents
    """
    answer = response["answer"]
    source_documents = response["source_documents"]
    links = [map_document_to_link(x) for x in source_documents]
    for i, link in enumerate(set(links)):
        answer += f"[[{i+1}]]({link})"
    return answer

def map_document_to_link(source_document: str) -> str:
    """
    Uses regular expressions to extract the visa number from the
    source document and map it to a link.
    """
    result = "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing"
    visa_number = re.match(r"(\d{3})", source_document)
    with open("../data/visa_mapping.json", "r") as f:
        mapping = json.load(f)
    
    if visa_number:
        if visa_number[0] in mapping.keys():
            result = mapping[visa_number[0]]
    
    return result
    


##### STREAMLIT APP #####
st.title("Australia's Department of Home Affairs - Virtual Assistant")

if "server_started" not in st.session_state:
    st.session_state['server_started'] = check_server()
    if st.session_state['server_started'] == False:
        start_server()
        st.session_state['server_started'] = True

if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "How may I assist you today?"
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Write a question related to Australian visas"):
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        response = get_answer(prompt, st.session_state.messages)
        full_response += parse_response(response)
        message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

## add a button that clears the chat
def clear_chat_history():
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "How may I assist you today?"
        }
    ]

st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

