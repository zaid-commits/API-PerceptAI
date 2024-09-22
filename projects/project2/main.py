from flask import Flask, jsonify
from flask_cors import CORS
import os
import subprocess

app = Flask(__name__)

# Enable CORS so the React frontend can make requests to this Flask backend
CORS(app)

# Path to your projects directory
PROJECTS_DIR = r'C:\Users\coeng\OneDrive\Desktop\PerceptAI\Src\perceptAI\projects'

@app.route('/')
def index():
    # List all directories in the projects directory
    projects = [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d))]
    
    # Return the project list as JSON
    return jsonify({'projects': projects})

@app.route('/run/<project_name>', methods=['GET'])
def run_project(project_name):
    project_path = os.path.join(PROJECTS_DIR, project_name, 'main.py')
    
    if os.path.exists(project_path):
        try:
            # Run the project using subprocess
            subprocess.Popen(['python', project_path], cwd=os.path.join(PROJECTS_DIR, project_name))
            return jsonify({'message': f'{project_name} is running...'})
        except Exception as e:
            return jsonify({'error': f'Failed to run {project_name}: {str(e)}'}), 500
    else:
        return jsonify({'error': f'Project {project_name} does not exist or main.py is missing.'}), 404

if __name__ == '__main__':
    app.run(debug=True)
