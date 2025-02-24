from flask import Flask, jsonify
from flask_cors import CORS
import os
import subprocess

app = Flask(__name__)

# CORS Enabled 
CORS(app)

# Path to your projects directory (use an environment variable for production)
PROJECTS_DIR = os.getenv('PROJECTS_DIR', os.path.join(os.path.dirname(__file__), 'projects'))

@app.route('/')
def index():
    # Project directory listing
    try:
        projects = [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d))]
        return jsonify({'projects': projects})
    except FileNotFoundError:
        return jsonify({'error': 'Projects directory not found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/run/<project_name>', methods=['GET'])
def run_project(project_name):
    project_path = os.path.join(PROJECTS_DIR, project_name, 'main.py')
    
    if os.path.exists(project_path):
        try:
            # Run the project using subprocess
            subprocess.Popen(['python', project_path], cwd=os.path.join(PROJECTS_DIR, project_name))
            return jsonify({'message': f'{project_name} is starting...'})
        except Exception as e:
            return jsonify({'error': f'Failed to run {project_name}: {str(e)}'}), 500
    else:
        return jsonify({'error': f'Project {project_name} does not exist or main.py is missing.'}), 404

if __name__ == '__main__':
    # Run the application
    app.run(host='0.0.0.0', port=5050)  # Change to your desired host and port
