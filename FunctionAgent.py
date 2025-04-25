from groq import Groq
import re, json
from models.api_1 import groq_api_key
from models.messages import messages
from Head.NewSpeak import speak
from Functions.image_generator import generate_images
from Functions.desktop_automation import (
    open_website, open_application, send_email, 
    schedule_event, play_music, control_device,
    save_scheduled_tasks, load_scheduled_tasks, check_scheduled_tasks
)
import threading
import time
import datetime
import traceback
import os

# Initialize Groq client with api key
client = Groq(api_key=groq_api_key)

# Function to interact with AI
def Ai(prompt):
    add_messages("user", prompt)
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama3-70b-8192"
    )
    response = chat_completion.choices[0].message.content
    add_messages("assistant", response)
    return response

# Helper function to add messages to the conversation history
def add_messages(role, content):
    messages.append({"role": role, "content": content})

def safe_speak(text):
    try:
        from Head.NewSpeak import speak
        speak(text)
    except Exception as e:
        print(f"Text-to-speech error (continuing without speech): {e}")

# Background task to check scheduled events
def check_scheduled_events():
    while True:
        try:
            check_scheduled_tasks()
        except Exception as e:
            print(f"Error checking scheduled tasks: {str(e)}")
        time.sleep(60)  # Check every minute

# Start the background task
scheduler_thread = threading.Thread(target=check_scheduled_events, daemon=True)
scheduler_thread.start()

# Load any existing scheduled tasks
try:
    load_scheduled_tasks()
except Exception as e:
    print(f"Error loading scheduled tasks: {str(e)}")

# Main interaction loop
while True:
    try:
        user_query = input(">> ")
        
        # Handle direct image generation command
        if any(user_query.lower().startswith(prefix) for prefix in [
            'generate image', 'create image', 'show me', 'generate', 'create an image',
            'make image', 'make an image', 'create a picture', 'generate a picture'
        ]):
            # Clean up the prompt
            prompt = user_query.lower()
            for prefix in [
                'generate image of ', 'create image of ', 'show me ',
                'generate ', 'create an image of ', 'make image of ',
                'make an image of ', 'create a picture of ',
                'generate a picture of '
            ]:
                if prompt.startswith(prefix):
                    prompt = prompt.replace(prefix, '', 1)
                    break
            prompt = prompt.strip()
            
            print("Generating image...")
            result = generate_images(prompt)
            print(f"AI: {result}")
            safe_speak(result)
            continue
            
        # Handle direct email command
        if user_query.lower().startswith(('send email', 'send an email')):
            try:
                # Extract email details from query
                if 'mail' not in user_query.lower() and 'to' not in user_query.lower():
                    raise ValueError("Please specify who to send the email to using 'to' or 'mail'")
                
                # Find email address using regex
                import re
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                email_match = re.search(email_pattern, user_query)
                
                if not email_match:
                    raise ValueError("Could not find a valid email address in your message")
                
                to_email = email_match.group(0)
                
                # Extract message
                if 'that' in user_query.lower():
                    message_parts = user_query.lower().split('that')[1].strip()
                else:
                    # Try to find the message after the email
                    message_parts = user_query.lower().split(to_email)[1].strip()
                    if message_parts.startswith(','):
                        message_parts = message_parts[1:].strip()
                
                if not message_parts:
                    raise ValueError("Please include a message to send")
                
                body = message_parts
                subject = "Message from JARVIS"
                
                # Validate email format
                if '@' not in to_email or '.' not in to_email:
                    raise ValueError("Invalid email address format")
                
                AiResponse = send_email(to_email, subject, body)
                print(f"AI: {AiResponse}")
                safe_speak(AiResponse)
                continue
            except Exception as e:
                error_msg = f"Error sending email: {str(e)}"
                print(f"AI: {error_msg}")
                safe_speak(error_msg)
                continue

        # Handle API key check command
        if user_query.lower() in ['check api key', 'what is my api key', 'api key status']:
            api_key = os.getenv('STABLE_DIFFUSION_API_KEY')
            if api_key:
                masked_key = f"{api_key[:4]}...{api_key[-4:]}"
                status = "API key is loaded" if api_key != "your-api-key-here" else "API key is still using placeholder text"
                print(f"\n=== API Key Status ===")
                print(f"Key: {masked_key}")
                print(f"Status: {status}")
                print(f"Length: {len(api_key)} characters")
                safe_speak(status)
            else:
                print("\n=== API Key Status ===")
                print("Error: No API key found in environment variables")
                safe_speak("No API key found in environment variables")
            continue

        # Get AI response for other commands
        res_json = Ai(user_query)

        # Clean up potential problematic characters
        res_json = re.sub(r'[\x00-\x1F]', '', res_json) 

        try:
            # Direct command handling for common applications and websites
            if user_query.lower().startswith(('open ', 'launch ')):
                command = user_query.lower().replace('open ', '').replace('launch ', '')
                
                # Handle website URLs
                if any(domain in command for domain in ['.com', '.org', '.net', '.edu', '.gov']):
                    if not command.startswith(('http://', 'https://')):
                        command = 'https://' + command
                    AiResponse = open_website(command)
                # Handle applications
                elif command == 'notepad':
                    AiResponse = open_application('notepad.exe')
                elif command == 'calculator':
                    AiResponse = open_application('calc.exe')
                elif command == 'chrome':
                    AiResponse = open_application('chrome.exe')
                elif command == 'word':
                    AiResponse = open_application('WINWORD.EXE')
                else:
                    AiResponse = open_application(command)
                print(f"AI: {AiResponse}")
                safe_speak(AiResponse)
                continue

            # Attempt to parse the string into a JSON dictionary
            res = json.loads(res_json)
            function_name = res.get("function_name", None)
            print(function_name)
            
            if "Desktop Automation" in function_name:
                action = res.get("action_details", {}).get("action", "")
                if "open_website" in action:
                    url = res.get("action_details", {}).get("url", "")
                    AiResponse = open_website(url)
                elif "open_app" in action:
                    app_name = res.get("action_details", {}).get("app_name", "")
                    AiResponse = open_application(app_name)
                elif "send_email" in action:
                    to_email = res.get("action_details", {}).get("to_email", "")
                    subject = res.get("action_details", {}).get("subject", "")
                    body = res.get("action_details", {}).get("body", "")
                    AiResponse = send_email(to_email, subject, body)
                elif "schedule_event" in action:
                    event_name = res.get("action_details", {}).get("event_name", "")
                    event_time = res.get("action_details", {}).get("event_time", "")
                    event_description = res.get("action_details", {}).get("description", "")
                    AiResponse = schedule_event(event_name, event_time, event_description)
                    save_scheduled_tasks()
                elif "play_music" in action:
                    file_path = res.get("action_details", {}).get("file_path", "")
                    AiResponse = play_music(file_path)
                elif "control_device" in action:
                    device_name = res.get("action_details", {}).get("device_name", "")
                    device_action = res.get("action_details", {}).get("action", "")
                    AiResponse = control_device(device_name, device_action)
                else:
                    AiResponse = "Unknown automation action"
            
            elif "Generate Image" in function_name:
                prompt = res.get("action_details", {}).get("user_query", user_query)   
                generate_images(prompt)
                AiResponse = "I've generated the image for you. You should see it open in a new window."
                
            else:
                AiResponse = res.get("response", None)
        except json.JSONDecodeError:
            # If the response is not JSON, treat it as a regular response
            AiResponse = res_json
        
        print(f"AI: {AiResponse}")
        safe_speak(AiResponse)
        
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        safe_speak(error_message)