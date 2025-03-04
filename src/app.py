from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

PROJECTS_DIR = os.getenv('PROJECTS_DIR', os.path.join(os.path.dirname(__file__), 'projects'))
os.makedirs(PROJECTS_DIR, exist_ok=True)

@app.route('/')
def index():
    """Fetches all OpenCV projects"""
    try:
        projects = []
        for d in os.listdir(PROJECTS_DIR):
            project_path = os.path.join(PROJECTS_DIR, d)
            if os.path.isdir(project_path):
                image_path = os.path.join(project_path, 'image.png')
                description_path = os.path.join(project_path, 'description.txt')

                # Read description if it exists
                description = None
                if os.path.exists(description_path):
                    with open(description_path, 'r', encoding='utf-8') as f:
                        description = f.read().strip()

                projects.append({
                    'name': d,
                    'image': f'/projects/{d}/image.png' if os.path.exists(image_path) else None,
                    'description': description
                })
        return jsonify({'projects': projects})
    except FileNotFoundError:
        return jsonify({'error': 'Projects directory not found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/projects/<project_name>/image.png')
def project_image(project_name):
    """Serves the project image"""
    project_path = os.path.join(PROJECTS_DIR, project_name)
    image_path = os.path.join(project_path, 'image.png')
    if os.path.exists(image_path):
        return send_from_directory(project_path, 'image.png')
    else:
        return jsonify({'error': 'Image not found.'}), 404

@app.route('/run/<project_name>', methods=['GET'])
def run_project(project_name):
    """Runs main.py of the given project"""
    project_path = os.path.join(PROJECTS_DIR, project_name, 'main.py')
    
    if os.path.exists(project_path):
        try:
            subprocess.Popen(['python', project_path], cwd=os.path.join(PROJECTS_DIR, project_name))
            return jsonify({'message': f'{project_name} is starting...'})
        except Exception as e:
            return jsonify({'error': f'Failed to run {project_name}: {str(e)}'}), 500
    else:
        return jsonify({'error': f'Project {project_name} does not exist or main.py is missing.'}), 404

@app.route('/opencv/project/submit', methods=['POST'])
def submit_opencv_project():
    """Handles OpenCV project submission"""
    if 'main.py' not in request.files or 'image.png' not in request.files or 'description.txt' not in request.files:
        return jsonify({"error": "Missing required files"}), 400

    project_name = request.form.get("project_name")
    if not project_name:
        return jsonify({"error": "Project name is required"}), 400

    # Create project folder
    project_folder = os.path.join(PROJECTS_DIR, secure_filename(project_name))
    os.makedirs(project_folder, exist_ok=True)

    # Save uploaded files
    request.files['main.py'].save(os.path.join(project_folder, "main.py"))
    request.files['image.png'].save(os.path.join(project_folder, "image.png"))
    request.files['description.txt'].save(os.path.join(project_folder, "description.txt"))

    return jsonify({"message": f"Project '{project_name}' submitted successfully!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
