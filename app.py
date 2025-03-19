import os
import time
import re
import markdown
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

def add_tailwind_classes(html):
    """Add Tailwind CSS classes to HTML elements to ensure proper styling"""
    
    # Add classes to headings
    html = re.sub(r'<h1>(.*?)</h1>', r'<h1 class="text-2xl font-bold mt-4 mb-2">\1</h1>', html)
    html = re.sub(r'<h2>(.*?)</h2>', r'<h2 class="text-xl font-bold mt-4 mb-2">\1</h2>', html)
    html = re.sub(r'<h3>(.*?)</h3>', r'<h3 class="text-lg font-bold mt-3 mb-2">\1</h3>', html)
    html = re.sub(r'<h4>(.*?)</h4>', r'<h4 class="text-base font-bold mt-3 mb-1">\1</h4>', html)
    
    # Add classes to paragraphs
    html = re.sub(r'<p>(.*?)</p>', r'<p class="mb-3">\1</p>', html)
    
    # Add classes to unordered lists
    html = re.sub(r'<ul>(.*?)</ul>', r'<ul class="list-disc ml-5 my-2 space-y-1">\1</ul>', html, flags=re.DOTALL)
    
    # Add classes to ordered lists
    html = re.sub(r'<ol>(.*?)</ol>', r'<ol class="list-decimal ml-5 my-2 space-y-1">\1</ol>', html, flags=re.DOTALL)
    
    # Add classes to list items
    html = re.sub(r'<li>(.*?)</li>', r'<li class="mb-1">\1</li>', html)
    
    # Add classes to blockquotes
    html = re.sub(r'<blockquote>(.*?)</blockquote>', 
                r'<blockquote class="border-l-4 border-indigo-500/50 pl-4 my-2 italic text-white/90">\1</blockquote>', 
                html, flags=re.DOTALL)
    
    # Add classes to links
    html = re.sub(r'<a href="(.*?)">(.*?)</a>', 
                r'<a href="\1" class="text-blue-400 underline hover:text-blue-300">\2</a>', 
                html)
    
    # Add classes to code blocks
    html = re.sub(r'<pre><code>(.*?)</code></pre>', 
                r'<pre class="bg-black/20 p-3 rounded-md overflow-x-auto my-3"><code class="font-mono text-sm">\1</code></pre>', 
                html, flags=re.DOTALL)
    
    # Add classes to inline code
    html = re.sub(r'<code>(.*?)</code>', 
                r'<code class="bg-black/20 px-1 py-0.5 rounded text-sm font-mono">\1</code>', 
                html)
    
    return html

def process_markdown(text):
    """Convert markdown to HTML and add Tailwind classes for styling"""
    # First convert markdown to HTML
    html = markdown.markdown(text)
    
    # Add Tailwind classes to HTML elements
    html = add_tailwind_classes(html)
    
    # Replace ** with <strong> tags for any that weren't caught
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong class="font-semibold">\1</strong>', html)
    
    # Replace * with <em> tags for any that weren't caught
    html = re.sub(r'\*(.*?)\*', r'<em class="italic">\1</em>', html)
    
    # Handle disclaimers with special styling
    html = re.sub(r'IMPORTANT DISCLAIMER:?(.*?)(?=<\/p>|$)', 
                r'<div class="mt-4 text-sm p-2 px-3 bg-white/5 rounded-lg text-white/70"><strong>Important Disclaimer:</strong>\1</div>', 
                html, flags=re.DOTALL|re.IGNORECASE)
    
    return html

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
                response_text = messages.data[0].content[0].text.value
                
                # Process markdown to HTML with Tailwind classes
                processed_response = process_markdown(response_text)

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
                    "response": processed_response,
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