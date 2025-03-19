import os
from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

load_dotenv()

openai_api_key=os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=openai_api_key)

app = Flask(__name__)

@app.route('/')
def chat():
    return render_template('chat.html')



assistant = client.beta.assistants.create(
  name="DR.ai",
  instructions="You are a health expert. You are chatting with auser who is looking for information on his/her health. Do whatever the user ask you to for their health.",
  tools=[{"type": "code_interpreter"}],
  model="gpt-4o",
)

# Initialize thread as None
thread = None

# Move thread creation to a function
@app.route('/new_chat', methods=['POST'])
def new_chat():
    global thread
    thread = client.beta.threads.create()
    return jsonify({"status": "success"}), 200

@app.route('/send_message', methods=['POST'])
def send_message():
    global thread
    # Create initial thread if none exists
    if thread is None:
        thread = client.beta.threads.create()
        
    user_message = request.json.get('message')
    request_prompts = request.json.get('requestPrompts', True)

    # Send user message
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )

    # Get response
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=os.environ.get("ASSISTANT_KEY"),
        instructions="You are a health expert. You are chatting with a user who is looking for information on his/her health. Do whatever the user ask you to for their health."
    )

    if run.status == 'completed':
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        response = messages.data[0].content[0].text.value

        # If prompts are requested, get related prompts
        related_prompts = []
        if request_prompts:
            prompt_message = client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content="Based on our conversation, what are 3 related questions the user might want to ask next? Respond only with the 3 questions in a list format. The question should not be more than 5/6 words"
            )
            prompt_run = client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=os.environ.get("ASSISTANT_KEY"),
            )
            if prompt_run.status == 'completed':
                prompt_messages = client.beta.threads.messages.list(thread_id=thread.id)
                prompts_text = prompt_messages.data[0].content[0].text.value
                related_prompts = [p.strip().strip('123.') for p in prompts_text.split('\n') if p.strip()][:3]
            
        print(related_prompts)
        return jsonify({
            "response": response,
            "relatedPrompts": related_prompts
        }), 200
    else:
        return jsonify({"response": "Processing...", "relatedPrompts": []}), 200


if __name__ == '__main__':
    app.run(debug=True)