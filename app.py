import os
import time
import base64
import re
import json
import threading

import streamlit as st
import openai
from tools import TOOL_MAP

st.set_page_config(page_icon="🤖", layout="wide")
openai_api_key = "add_your_openai_api_key_here"
client = None
client = openai.OpenAI(api_key=openai_api_key)
assistant_id = "add_your_assistant_id_here"
instructions = os.environ.get("RUN_INSTRUCTIONS", "")
assistant_title = os.environ.get("ASSISTANT_TITLE", "Dr.ai")


def create_thread(content, file):
    messages = [
        {
            "role": "user",
            "content": content,
        }
    ]
    if file is not None:
        messages[0].update({"file_ids": [file.id]})
    thread = client.beta.threads.create(messages=messages)
    return thread


def create_message(thread, content, file):
    message = [
        {
            "role": "user",
            "content": content,
        }
    ]
    if file is not None:
        message[0].update({"file_ids": [file.id]})
    client.beta.threads.messages.create(thread_id=thread.id, role="user", content=content)


def create_run(thread):
    run = client.beta.threads.runs.create(
        thread_id=thread.id, assistant_id=assistant_id, instructions=instructions
    )
    return run


def get_message_value_list(messages):
    #message_content = ""
    message_value_list = []
    for message in messages:
        if message.role == "assistant":
            if message.content and len(message.content) > 0:  # Check if message.content is not empty
                message_content = str(message.content[0].text.value)  # Access the 'text' attribute
                message_value_list.append(message_content)
    return message_value_list


def get_message_list(thread, run):
    completed = False
    while not completed:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        if run.status == "completed":
            completed = True
        elif run.status == "failed":
            break
        else:
            time.sleep(1)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return get_message_value_list(messages)


def get_response(user_input):
    if "thread" not in st.session_state:
        st.session_state.thread = create_thread(user_input, None)
    else:
        create_message(st.session_state.thread, user_input, None)
    run = create_run(st.session_state.thread)
    run = client.beta.threads.runs.retrieve(
        thread_id=st.session_state.thread.id, run_id=run.id
    )

    while run.status == "in_progress":

        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread.id, run_id=run.id
        )
        run_steps = client.beta.threads.runs.steps.list(
            thread_id=st.session_state.thread.id, run_id=run.id
        )
        for step in run_steps.data:
            if hasattr(step.step_details, "tool_calls"):
                for tool_call in step.step_details.tool_calls:
                        if run.status == "requires_action":
                            print("run.status:", run.status)
        run = execute_action(run, st.session_state.thread)

        count = 0


    return get_message_list(st.session_state.thread, run)[0]


def execute_action(run, thread):
    tool_outputs = []
    if run.status == "requires_action":
        if run.required_action.submit_tool_outputs is not None: 
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                tool_id = tool_call.id
                tool_function_name = tool_call.function.name

                tool_function_arguments = json.loads(tool_call.function.arguments)


                tool_function_output = TOOL_MAP[tool_function_name](**tool_function_arguments)
                tool_outputs.append({"tool_call_id": tool_id, "output": tool_function_output})

        run = client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread.id,
        run_id=run.id,
        tool_outputs=tool_outputs,
    )
    return run


def handle_uploaded_file(uploaded_file):
    file = client.files.create(file=uploaded_file, purpose="assistants")
    return file


def render_chat():
    for chat in st.session_state.chat_log:
        with st.chat_message(chat["name"]):
            st.markdown(chat["msg"], True)


if "tool_call" not in st.session_state:
    st.session_state.tool_calls = []

if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

if "in_progress" not in st.session_state:
    st.session_state.in_progress = False


def disable_form():
    st.session_state.in_progress = True


def main():

    css = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@100..900&display=swap');
        body {
            background-image: linear-gradient(to right, red , yellow); !important;
        }
        .stMarkdown h1 {
            font-family: "Poppins";
            font-size: 11em;
            font-weight: 700;
            color: #FFFFFF;
            text-align: center;
            text-shadow: 0 0 0.4em #ffffff, 0 0 0.5em #ffffff, 0 0 0.25em #ffffff;
            filter: progid:DXImageTransform.Microsoft.Glow(strength=5, Color=#ffffff);

        }
        .stMarkdown h2 {
            font-family: "Poppins";
            color: #FDFDFD;
            font-size: 2em;
            text-align: center;
            text-shadow: 1px 1px 0 #000, -1px -1px 0 #000;
            text-decoration: underline;
        }

        .stMarkdown p {
            font-family: "Poppins";
            font-size: 1em;
            color: #FFFFFF;
        }

        div[data-baseweb="sideNav"] > div {
            background-color: #000000;
        
    """

    st.markdown(css, unsafe_allow_html=True)
    
    st.markdown(f'<h1>{assistant_title}</h1>', unsafe_allow_html=True)
    st.markdown('<h2>Your personal health assistant</h2>', unsafe_allow_html=True)
    user_msg = st.chat_input(
        "Message", on_submit=disable_form, disabled=st.session_state.in_progress
    )
    
    if user_msg:
        render_chat()
        with st.chat_message("user"):
            st.markdown(user_msg, True)
        st.session_state.chat_log.append({"name": "user", "msg": user_msg})
        with st.spinner("Wait for response..."):
            response = get_response(user_msg)
        with st.chat_message("Assistant"):
            st.markdown(response, True)

        st.session_state.chat_log.append({"name": "assistant", "msg": response})
        st.session_state.in_progress = False
        st.session_state.tool_call = None
        st.rerun()
    render_chat()

    if st.sidebar.button('Start new chat'):
    # Start a new thread when the button is clicked
        if "thread" in st.session_state:
            del st.session_state.thread
        st.session_state.chat_log = []
        st.experimental_rerun()
        


if __name__ == "__main__":
    main()
