import os
import logging
import subprocess
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load environment variables from .env file
load_dotenv()

PROJECTS_DIR = os.getenv('PROJECTS_DIR')

@app.route('/projects', methods=['GET'])
def list_projects():
    try:
        projects = [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d))]
        return jsonify({'projects': projects})
    except Exception as e:
        logging.error(f"Failed to list projects: {str(e)}")
        return jsonify({'error': f'Failed to list projects: {str(e)}'}), 500

@app.route('/run_project/<project_name>', methods=['POST'])
def run_project(project_name):
    project_path = os.path.join(PROJECTS_DIR, project_name, 'main.py')
    if os.path.exists(project_path):
        try:
            logging.info(f"Running project: {project_name} at {project_path}")
            process = subprocess.Popen(
                ['python', project_path],
                cwd=os.path.join(PROJECTS_DIR, project_name),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            if stdout:
                logging.info(f"Output: {stdout}")
            if stderr:
                logging.error(f"Error: {stderr}")
            return jsonify({'message': f'{project_name} is starting...', 'output': stdout, 'error': stderr})
        except Exception as e:
            logging.error(f"Failed to run {project_name}: {str(e)}")
            return jsonify({'error': f'Failed to run {project_name}: {str(e)}'}), 500
    else:
        return jsonify({'error': f'Project {project_name} does not exist or main.py is missing.'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)