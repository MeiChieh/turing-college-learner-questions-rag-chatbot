import streamlit as st
import requests
import time
from helper.streamlit_helper_functions import (
    set_initial_st_state,
    send_first_message,
    clean_chat_history,
    has_param_changed,
)
import markdown

initial_state_dict = {
    "llm_params_curr": {
        "temperature": 0.3,
        "top_p": 0.3,
        "max_tokens": 1000,
    },
    "llm_params_prev": {
        "temperature": 0.3,
        "top_p": 0.3,
        "max_tokens": 1000,
    },
    "valid_api_key": False,
    "is_first_msg": True,
    "messages": [],
    "is_streaming": False
}

st.session_state = set_initial_st_state(st.session_state, initial_state_dict)

st.subheader("🤖 Welcome to Turing College Knowledge bot")
st.write("I am here to answer your Turing College learning related questions.")
st.write(
    "My knowledge is based on the [TC confluence pages](https://turingcollege.atlassian.net/wiki/spaces/DLG/overview)."
)

# api key in sidebar
api_key = st.sidebar.text_input(
    "🔑 OpenAI API Key", type="password", disabled=st.session_state["valid_api_key"]
)

# api key validation
if not st.session_state["valid_api_key"]:

    if api_key:

        api_key_validation_response = requests.post(
            "http://127.0.0.1:8000/set_api_key", json={"api_key": api_key}
        )

        api_key_is_valid = api_key_validation_response.json()["valid_api_key"]

        if api_key_is_valid:
            st.session_state["valid_api_key"] = True
            message_placeholder = st.empty()
            message_placeholder.success(
                "API key is valid! We can start with the chat!", icon="✅"
            )
            time.sleep(1)
            st.rerun()  # trigger rerender to disable api key entry field

        else:
            st.session_state["valid_api_key"] = False
            message_placeholder = st.empty()
            message_placeholder.warning(
                "API key is invalid! Please enter a valid API key.", icon="⚠️"
            )
            time.sleep(5)
            message_placeholder.empty()

    else:
        st.warning(
            "Please provide your OpenAI API key **in the side panel** to start the chat.",
            icon="🔑",
        )

# don't render the rest of the app without valid_api_key
if not st.session_state["valid_api_key"]:
    st.stop()

# sliders for llm params

temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        step=0.1,
        value=st.session_state["llm_params_curr"]["temperature"],
        help="Controls the creativity and focus of the model.",
    )

top_p = st.sidebar.slider(
    "Top-P",
    min_value=0.0,
    max_value=1.0,
    step=0.1,
    value=st.session_state["llm_params_curr"]["top_p"],
    help="Controls the randomness of the model's output.",
)

max_tokens = st.sidebar.slider(
    "Max Tokens",
    min_value=0,
    max_value=1000,
    step=10,
    value=st.session_state["llm_params_curr"]["max_tokens"],
    help="Controls the length of the generated text.",
)

# update llm params when sliders are changed
st.session_state["llm_params_prev"] = has_param_changed(
    "temperature",
    temperature,
    st.session_state["llm_params_curr"],
    st.session_state["llm_params_prev"],
)

st.session_state["llm_params_prev"] = has_param_changed(
    "top_p",
    top_p,
    st.session_state["llm_params_curr"],
    st.session_state["llm_params_prev"],
)
st.session_state["llm_params_prev"] = has_param_changed(
    "max_tokens",
    max_tokens,
    st.session_state["llm_params_curr"],
    st.session_state["llm_params_prev"],
)

# restart chat
st.sidebar.button(
    "Restart Chat",
    on_click=lambda: clean_chat_history(st.session_state),
    help="Clean the chat history and settings and restart a new chat.",
)

# render first chat from the assistant
if st.session_state.is_first_msg:
    st.session_state.messages = send_first_message(st.session_state.messages)
    st.session_state.is_first_msg = False

# render all chats from the state
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message["avatar"]):
        st.markdown(message["content"], unsafe_allow_html=True)


if prompt := st.chat_input("Your questions go here!"):
    st.session_state.is_streaming = True
    st.session_state.messages.append(
        {"role": "user", "content": prompt, "avatar": "👩🏻‍💻"}
    )
    with st.chat_message("user", avatar="👩🏻‍💻"):
        st.markdown(prompt)

    # In the assistant's message, stream the response
    with st.chat_message("assistant", avatar="🤖"):

        assistant_placeholder = st.empty()
        full_response = ""

        stream = requests.post(
            "http://127.0.0.1:8000/chat",
            json={"human_msg": prompt},
            stream=True,
        )

        for chunk in stream.iter_lines(decode_unicode=True):

            if chunk:
                full_response += markdown.markdown(chunk)

                assistant_placeholder.markdown(full_response, unsafe_allow_html=True)
                time.sleep(0.07)
    st.session_state.is_streaming = False
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response, "avatar": "🤖"}
    )
