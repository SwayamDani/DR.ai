import os
import time
import json
import streamlit as st
import openai
from tools import TOOL_MAP

st.set_page_config(page_icon="🤖", layout="wide")
openai_api_key = "Add_Your_API_Key_Here"
client = None
client = openai.OpenAI(api_key=openai_api_key)
assistant_id = "Add_Your_Assistant_ID_Here"
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

# Define function to create messages
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

# Define function to create runs
def create_run(thread):
    run = client.beta.threads.runs.create(
        thread_id=thread.id, assistant_id=assistant_id, instructions=instructions
    )
    return run

# Define function to get message value list
def get_message_value_list(messages):
    message_value_list = []
    for message in messages:
        if message.role == "assistant":
            if message.content and len(message.content) > 0:  
                message_content = str(message.content[0].text.value) 
                message_value_list.append(message_content)
    return message_value_list

# Define function to get message list
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

# Define function to get response
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

    return get_message_list(st.session_state.thread, run)[0]

# Define function to execute action
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

    file = client.files.create(file=uploaded_file, purpose="assistants")
    return file

# Define function to render chat
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

css = """
    <style>
        
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@100..900&display=swap');
        
        .stMarkdown h1 {
            font-family: "Poppins";
            font-size: 10.5em;
            font-weight: 700;
            color: #FFFFFF;
            text-align: center;
            text-shadow: 0 0 0.4em #ffffff, 0 0 0.5em #ffffff, 0 0 0.25em #ffffff;
            filter: progid:DXImageTransform.Microsoft.Glow(strength=5, Color=#ffffff);
        }

        .stMarkdown h3 {
            font-family: "Poppins";
            font-size: 1.5em;
            color: #FFFFFF;
            text-align: center;
            padding-bottom: 0;
        }

        .stMarkdown h4 {
            font-family: "Poppins";
            font-size: 1.2em;
            color: #FFFFFF;
            text-align: center;
        }

        .stMarkdown p {
            font-family: "Poppins";
            font-size: 1.2em;
            color: #FFFFFF;
        }

        .stButton>button {
            color: white;
            border: none;
            text-align: center;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: auto;
            transition-duration: 0.4s;
        }

        .stButton>button:hover {
            box-shadow: 0 0 0.4em #ffffff, 0 0 0.5em #ffffff, 0 0 0.25em #ffffff;
            filter: progid:DXImageTransform.Microsoft.Glow(strength=5, Color=#ffffff);
        } 

        .st-bb {
            border-color: red !important;
        }

        .stChatMessage {
        font-family: "Poppins";
        background-color: #000000 !important;
        color: black !important;

        .reportview-container {
            font-family: 'Poppins' !important;
        }
    }
    """

st.markdown(css, unsafe_allow_html=True)
def main():
    st.title("Dr.ai")

    
    if st.sidebar.button('Start new chat'):
         if "thread" in st.session_state:
            del st.session_state.thread
         st.session_state.chat_log = []
         st.experimental_rerun()




    

    st.sidebar.markdown("""
    <br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>
    <h4>Made with ❤️ by Swayam Dani</h4>
    <h4>Connect with me:</h4>
    <table style="width:100%; border: 0;">
        <tr>
            <td style="text-align:center; border: 0;">
                <a href="https://github.com/tannicflux">
                    <img src="https://tannicflux.github.io/assets/img/GitHub_Logo_White.png" alt = "GITHUB" width="50px">
                </a>
            </td>
            <td style="text-align:center; border: 0;">
                <a href="https://www.linkedin.com/in/swayam-dani">
                    <img src="https://tannicflux.github.io/assets/img/LI-In-Bug.png" alt = "LINKEDIN" width="30px">
                </a>
            </td>
            <td style="text-align:center; border: 0;">
                <a href="mailto:swayamashishdani@gmail.com">
                    <img src="https://tannicflux.github.io/assets/img/Gmail_Logo_512px.png" alt = "EMAIL" width="30px">
                </a>
            </td>
        </tr>
    </table>
    """, unsafe_allow_html=True)
    #st.markdown(f"# [{assistant_title}](https://tannicflux.github.io)", unsafe_allow_html=True)

    prompts = {
    "How do I loose weight?",
    "Write a creative story",
    "Translate a sentence"
    }

    # Create columns for each prompt
    columns = st.columns([2, 5, 4, 5, 4, 5])

    # Create buttons in each column
    for i, prompt in enumerate(prompts):
        if columns[i*2+1].button(prompt):
            # Set user_msg to the prompt when the button is clicked
            user_msg = prompt
            break
    else:
        user_msg = st.chat_input(
            "Message", on_submit=disable_form, disabled=st.session_state.in_progress
        )    
    if user_msg:
        render_chat()
        with st.chat_message("user"):
            st.markdown("Clone Repository and add you API_KEY, ASSISTANT_ID. Also uncomment the code lines in main", True)
        #st.session_state.chat_log.append({"name": "user", "msg": user_msg})
        #with st.spinner("Wait for response..."):
        #    response = get_response(user_msg)
        #with st.chat_message("Assistant"):
        #    st.markdown(response, True)

        #st.session_state.chat_log.append({"name": "assistant", "msg": response})
        #st.session_state.in_progress = False
        #st.session_state.tool_call = None
        #st.rerun()

    render_chat()

    

if __name__ == "__main__":
    main()
