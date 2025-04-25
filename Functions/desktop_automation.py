import webbrowser
import os
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import pyautogui
import datetime
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Store scheduled tasks
scheduled_tasks = {}

def open_website(url):
    """Open a website in the default browser"""
    try:
        webbrowser.open(url)
        return f"Opening website: {url}"
    except Exception as e:
        return f"Error opening website: {str(e)}"

def open_application(app_name):
    """Open a desktop application or common website"""
    try:
        # Common website mappings
        website_mappings = {
            'youtube': 'https://www.youtube.com',
            'google': 'https://www.google.com',
            'gmail': 'https://mail.google.com',
            'facebook': 'https://www.facebook.com',
            'twitter': 'https://twitter.com',
            'linkedin': 'https://www.linkedin.com'
        }
        
        # Check if it's a common website
        app_lower = app_name.lower()
        if app_lower in website_mappings:
            webbrowser.open(website_mappings[app_lower])
            return f"Opening website: {website_mappings[app_lower]}"
            
        # Handle Windows applications
        if os.name == 'nt':  # Windows
            common_apps = {
                'notepad': 'notepad.exe',
                'calculator': 'calc.exe',
                'paint': 'mspaint.exe',
                'chrome': 'chrome.exe',
                'firefox': 'firefox.exe',
                'edge': 'msedge.exe'
            }
            
            if app_lower in common_apps:
                app_name = common_apps[app_lower]
            
            try:
                # Try using start command which is more reliable on Windows
                subprocess.Popen(['start', app_name], shell=True)
                return f"Opening application: {app_name}"
            except Exception as e:
                return f"Could not find the application '{app_name}'. Please make sure it is installed."
        else:  # Linux/Mac
            subprocess.Popen(['open', app_name])
            return f"Opening application: {app_name}"
    except Exception as e:
        return f"Error: {str(e)}"

def send_email(to_email, subject, body):
    """Send an email using SMTP"""
    try:
        # Validate input parameters
        if not to_email or not isinstance(to_email, str):
            return "Error: Invalid recipient email address"
        if not subject or not isinstance(subject, str):
            return "Error: Invalid email subject"
        if not body or not isinstance(body, str):
            return "Error: Invalid email body"

        # Get credentials from environment variables
        sender_email = os.getenv('EMAIL')
        sender_password = os.getenv('PASSWORD')
        smtp_server = os.getenv('SMTP_URL', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))

        # Check if credentials are set
        if not sender_email:
            return "Error: EMAIL not found in .env file"
        if not sender_password:
            return "Error: PASSWORD not found in .env file"

        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send email
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            return f"Email sent successfully to {to_email}"
            
        except smtplib.SMTPAuthenticationError:
            return "Error: Invalid email credentials. Please check your email and password in the .env file"
        except smtplib.SMTPException as e:
            return f"Error sending email: {str(e)}"
        except Exception as e:
            return f"Error connecting to email server: {str(e)}"

    except Exception as e:
        return f"Error preparing email: {str(e)}"

def schedule_event(event_name, event_time, event_description):
    """Schedule an event"""
    try:
        scheduled_tasks[event_name] = {
            'time': event_time,
            'description': event_description
        }
        return f"Event '{event_name}' scheduled for {event_time}"
    except Exception as e:
        return f"Error scheduling event: {str(e)}"

def play_music(file_path):
    """Play music from a file"""
    try:
        if os.name == 'nt':  # Windows
            os.startfile(file_path)
        else:  # Linux/Mac
            subprocess.Popen(['open', file_path])
        return f"Playing music: {file_path}"
    except Exception as e:
        return f"Error playing music: {str(e)}"

def control_device(device_name, action):
    """Control a smart device (placeholder for future implementation)"""
    try:
        # This is a placeholder for actual device control implementation
        return f"Controlling device {device_name} with action {action}"
    except Exception as e:
        return f"Error controlling device: {str(e)}"

def save_scheduled_tasks():
    """Save scheduled tasks to a file"""
    try:
        with open('scheduled_tasks.json', 'w') as f:
            json.dump(scheduled_tasks, f)
        return "Scheduled tasks saved successfully"
    except Exception as e:
        return f"Error saving scheduled tasks: {str(e)}"

def load_scheduled_tasks():
    """Load scheduled tasks from a file"""
    try:
        if Path('scheduled_tasks.json').exists():
            with open('scheduled_tasks.json', 'r') as f:
                global scheduled_tasks
                scheduled_tasks = json.load(f)
            return "Scheduled tasks loaded successfully"
        return "No scheduled tasks found"
    except Exception as e:
        return f"Error loading scheduled tasks: {str(e)}"

def check_scheduled_tasks():
    """Check and execute scheduled tasks"""
    try:
        current_time = datetime.datetime.now().strftime("%H:%M")
        for event_name, event_data in scheduled_tasks.items():
            if event_data['time'] == current_time:
                # Execute the scheduled task
                print(f"Executing scheduled task: {event_name}")
                print(f"Description: {event_data['description']}")
                # You can add more specific task execution logic here
    except Exception as e:
        print(f"Error checking scheduled tasks: {str(e)}") 