import os
import time
from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session
import traceback

# Load environment variables
load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")
assistant_id = os.environ.get("ASSISTANT_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for sessions

# Define health assistant instructions with more detailed guidance
HEALTH_ASSISTANT_INSTRUCTIONS = """
You are Dr.ai, an AI health assistant designed to provide helpful, accurate health information.

GUIDELINES:
1. Provide clear, evidence-based health information when possible
2. Use compassionate, conversational language that's easy to understand
3. Avoid medical jargon unless necessary, and explain terms when you use them
4. Break down complex health concepts into manageable parts
5. Recommend seeking professional medical advice for specific diagnoses or treatment
6. Clearly distinguish between established medical facts and areas with ongoing research
7. Format responses with appropriate headings, bullet points, and spacing for readability
8. Be especially cautious about medication recommendations or dosages
9. For lifestyle questions, provide practical, actionable advice when appropriate
10. ALWAYS include a brief disclaimer for serious health concerns

IMPORTANT DISCLAIMER: Always make it clear that you are an AI assistant providing general information, not a licensed healthcare professional. Emphasize that your responses should not replace professional medical advice, diagnosis, or treatment.
"""

# Create health assistant if it doesn't exist
try:
    assistant = client.beta.assistants.create(
        name="DR.ai",
        instructions=HEALTH_ASSISTANT_INSTRUCTIONS,
        tools=[{"type": "code_interpreter"}],
        model="gpt-4o",
    )
except Exception as e:
    print(f"Error creating assistant: {str(e)}")
    # Fallback to using existing assistant ID if creation fails
    assistant = {"id": assistant_id}

# Dictionary to store active threads
active_threads = {}

@app.route('/')
def chat():
    return render_template('chat.html')

@app.route('/new_chat', methods=['POST'])
def new_chat():
    try:
        # Create a new thread
        thread = client.beta.threads.create()
        
        # Store thread ID in session
        session['thread_id'] = thread.id
        
        # Add to active threads with timestamp
        active_threads[thread.id] = {
            "created_at": time.time(),
            "last_active": time.time()
        }
        
        # Clean up old threads (older than 24 hours)
        cleanup_old_threads()
        
        return jsonify({"status": "success", "thread_id": thread.id}), 200
    except Exception as e:
        print(f"Error creating new chat: {str(e)}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Failed to create new chat"}), 500

def cleanup_old_threads():
    """Remove threads older than 24 hours"""
    current_time = time.time()
    thread_ids_to_remove = []
    
    for thread_id, thread_data in active_threads.items():
        # If thread is older than 24 hours (86400 seconds)
        if current_time - thread_data["created_at"] > 86400:
            thread_ids_to_remove.append(thread_id)
    
    # Remove old threads
    for thread_id in thread_ids_to_remove:
        try:
            active_threads.pop(thread_id, None)
        except Exception as e:
            print(f"Error removing thread {thread_id}: {str(e)}")

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        # Get thread ID from session, or create new thread if none exists
        thread_id = session.get('thread_id')
        if not thread_id:
            thread = client.beta.threads.create()
            thread_id = thread.id
            session['thread_id'] = thread_id
            active_threads[thread_id] = {
                "created_at": time.time(),
                "last_active": time.time()
            }
        
        # Update last active timestamp
        if thread_id in active_threads:
            active_threads[thread_id]["last_active"] = time.time()
        
        user_message = request.json.get('message')
        request_prompts = request.json.get('requestPrompts', True)
        
        # Send user message
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )

        # Get response with improved error handling
        try:
            run = client.beta.threads.runs.create_and_poll(
                thread_id=thread_id,
                assistant_id=assistant.id if hasattr(assistant, 'id') else assistant_id,
                instructions=HEALTH_ASSISTANT_INSTRUCTIONS
            )

            if run.status == 'completed':
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                response = messages.data[0].content[0].text.value

                # If prompts are requested, get related prompts
                related_prompts = []
                if request_prompts:
                    try:
                        prompt_message = client.beta.threads.messages.create(
                            thread_id=thread_id,
                            role="user",
                            content="Based on our conversation, suggest 3 specific follow-up questions that might be helpful. Respond with just the questions in a list format. Keep each question concise (under 6 words if possible)."
                        )
                        
                        prompt_run = client.beta.threads.runs.create_and_poll(
                            thread_id=thread_id,
                            assistant_id=assistant.id if hasattr(assistant, 'id') else assistant_id,
                        )
                        
                        if prompt_run.status == 'completed':
                            prompt_messages = client.beta.threads.messages.list(thread_id=thread_id)
                            prompts_text = prompt_messages.data[0].content[0].text.value
                            
                            # Improved prompt parsing
                            import re
                            # Look for numbered items or bullet points
                            prompts = re.findall(r'(?:^|\n)\s*(?:\d+\.|\*|\-)\s*(.*?)(?:\n|$)', prompts_text)
                            
                            # If no structured format, just split by newlines
                            if not prompts:
                                prompts = [p.strip() for p in prompts_text.split('\n') if p.strip()]
                            
                            # Take up to 3 prompts
                            related_prompts = prompts[:3]
                            
                    except Exception as e:
                        print(f"Error generating prompts: {str(e)}")
                        related_prompts = []
                
                return jsonify({
                    "response": response,
                    "relatedPrompts": related_prompts
                }), 200
            else:
                return jsonify({"response": f"An error occurred: {run.status}", "relatedPrompts": []}), 200
                
        except Exception as e:
            print(f"Error in processing message: {str(e)}")
            traceback.print_exc()
            return jsonify({"response": "I'm having trouble processing your request. Please try again.", "relatedPrompts": []}), 500
            
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        traceback.print_exc()
        return jsonify({"response": "An error occurred while processing your message. Please try again later.", "relatedPrompts": []}), 500