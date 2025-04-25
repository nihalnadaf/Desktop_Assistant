import os
import requests
from PIL import Image
from io import BytesIO
from pathlib import Path
import datetime
from dotenv import load_dotenv
import subprocess
import base64
import traceback
from PIL import ImageDraw

# Load environment variables
load_dotenv()

def generate_images(prompt):
    try:
        # Get the absolute path to the project directory
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Create images directory in the project root
        images_dir = os.path.join(project_dir, "generated_images")
        os.makedirs(images_dir, exist_ok=True)

        # Get the API key from environment variable
        api_key = os.getenv('STABLE_DIFFUSION_API_KEY')
        if not api_key or api_key == "your-api-key-here":
            return "Error: Please set your Stable Diffusion API key in the .env file"

        # Stable Diffusion API endpoint
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Request body
        body = {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "steps": 30,
            "samples": 1,
        }

        # Make the API request
        response = requests.post(url, headers=headers, json=body, timeout=30)
        
        if response.status_code != 200:
            return f"Error: API request failed with status code {response.status_code}"

        # Process the response
        response_json = response.json()
        
        if "artifacts" not in response_json or not response_json["artifacts"]:
            return "Error: No image data in API response"
            
        image_data = base64.b64decode(response_json["artifacts"][0]["base64"])
        
        # Save the image
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(images_dir, f"generated_image_{timestamp}.png")
        
        with open(image_path, "wb") as f:
            f.write(image_data)
        
        # Open the image
        open_image(image_path)
        
        return "Image generated successfully!"
            
    except Exception as e:
        return f"Error generating image: {str(e)}"
        
def open_image(image_path):
    try:
        if os.name == 'nt':  # Windows
            os.startfile(image_path)
        else:  # macOS and Linux
            subprocess.run(['xdg-open', image_path])
    except Exception as e:
        pass  # Silently fail if image can't be opened
        
        
