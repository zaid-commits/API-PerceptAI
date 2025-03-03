from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import subprocess
import google.generativeai as genai
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CORS
CORS(app)

# Path to projects directory (use environment variable for production)
PROJECTS_DIR = os.getenv('PROJECTS_DIR', os.path.join(os.path.dirname(__file__), 'projects'))

# Configure Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

conversation_history = []  # Store chat history


# -------------------- Project Management Endpoints --------------------

@app.route('/')
def index():
    """List all available projects in the directory."""
    try:
        projects = []
        for d in os.listdir(PROJECTS_DIR):
            project_path = os.path.join(PROJECTS_DIR, d)
            if os.path.isdir(project_path):
                image_path = os.path.join(project_path, 'image.png')
                projects.append({
                    'name': d,
                    'image': f'/projects/{d}/image.png' if os.path.exists(image_path) else None
                })
        return jsonify({'projects': projects})
    except FileNotFoundError:
        return jsonify({'error': 'Projects directory not found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/projects/<project_name>/image.png')
def project_image(project_name):
    """Serve the project preview image if available."""
    project_path = os.path.join(PROJECTS_DIR, project_name)
    image_path = os.path.join(project_path, 'image.png')
    if os.path.exists(image_path):
        return send_from_directory(project_path, 'image.png')
    else:
        return jsonify({'error': 'Image not found.'}), 404


@app.route('/run/<project_name>', methods=['GET'])
def run_project(project_name):
    """Run the specified OpenCV Python project."""
    project_path = os.path.join(PROJECTS_DIR, project_name, 'main.py')

    if os.path.exists(project_path):
        try:
            # Start project script
            subprocess.Popen(['python', project_path], cwd=os.path.join(PROJECTS_DIR, project_name))
            return jsonify({'message': f'{project_name} is starting...'})
        except Exception as e:
            return jsonify({'error': f'Failed to run {project_name}: {str(e)}'}), 500
    else:
        return jsonify({'error': f'Project {project_name} does not exist or main.py is missing.'}), 404


# -------------------- AI Chatbot Endpoints --------------------

@app.route('/chat', methods=['POST'])
def chat():
    """Process user input and respond using AI (Gemini API)."""
    global conversation_history
    user_input = request.json.get('user_input')
    
    if not user_input:
        return jsonify({'error': 'No user input received'}), 400
    
    print("User input:", user_input)  # Debug log

    # AI Context Setup
    context = (
        "You are an AI assistant named ImpicAI, developed by Zaid Rakhange at Impic. "
        "Impic is a tech community for developers, freelancers, and tech enthusiasts. "
        "The community link is https://community.impic.tech. "
        "Respond with relevant insights and concise answers based on previous conversations."
        "you should only help the user with the opencv question else say leave.!."
    )
    
    conversation_history.append(f"User: {user_input}")
    
    # Form full AI prompt
    full_prompt = f"{context}\n\nConversation History:\n" + "\n".join(conversation_history)

    # Generate AI response
    try:
        response = model.generate_content(full_prompt)
        print("Gemini API response:", response)  # Debug log

        ai_response = response.text
        ai_response = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', ai_response)  # Bold formatting
        ai_response = re.sub(r'<b>(.*?)</b>\*', r'<b>\1</b>\n', ai_response)  # Newline after bold text
        
        conversation_history.append(f"ImpicAI: {ai_response}")
        return jsonify({'response': ai_response})

    except Exception as e:
        return jsonify({'error': f'AI processing failed: {str(e)}'}), 500


# -------------------- Server Startup --------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)  # Change port if needed
