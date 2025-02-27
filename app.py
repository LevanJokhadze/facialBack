import os
import json
import yk_face as YKF
from dotenv import load_dotenv
from flask_cors import CORS
from flask import Flask, render_template, jsonify, request
import verify
# Load environment variables
load_dotenv()
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "https://facial-app-demo.netlify.app", "http://localhost:5173"])

KEY = os.getenv("YOUVERSE")  # or your hard-coded key
YKF.Key.set(KEY)

BASE_URL = os.getenv("BASE_URL")  # or your hard-coded URL
YKF.BaseUrl.set(BASE_URL)

@app.route('/')
def home():
    return 'Hello, World!'


UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check if the file has a valid extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/save', methods=['POST'])
def save():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    
    name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    age = request.form.get('age')

    filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filename)
    template = process_image(filename)
    if save_user_data_to_json(name, last_name, age, template):
        return jsonify({"success": "Uploaded Succesfully"})
    else:
        return jsonify({"error": "No Upload :9"})
        

# Route to upload the image
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    
    if file and allowed_file(file.filename):
        # Save the file
        name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        age = request.form.get('age')
        
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        template = process_image(filename)
        detect = verify.verify(template)

        if detect:
            return jsonify({"status": "success", "message": detect}), 200
        
        return jsonify({"error": "Face not found"}), 401


    
    return jsonify({"error": "Invalid file format"}), 400


# Function to process the image (detect and extract face template)
def process_image(image):
    # Perform face detection and analysis on the image
    detected_faces = YKF.face.process(image=image, processings=["detect", "analyze", "templify"])

    if detected_faces[0]:
        # Return the detected faces
        return detected_faces[0]['template']
        

def save_user_data_to_json(name, last_name, age, template):
    # Path to the JSON file where templates are stored
    templates_file = "templates.json"
    
    if os.path.exists(templates_file):
        with open(templates_file, "r") as file:
            templates = json.load(file)
    else:
        templates = []

    # Extract the template from the detected face
        # Prepare the new user data with template
    user_data = {
            'name': name,
            'last_name': last_name,
            'age': age,
            'template': template
    }
    templates.append(user_data)

    # Save the updated templates list back to the JSON file.
    with open(templates_file, "w") as file:
        json.dump(templates, file, indent=2)
    
    return user_data

# Define a route that renders an HTML template (if you use templates)
@app.route('/hello/<name>')
def hello(name):
    return render_template('hello.html', name=name)

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=os.getenv('PORT', 5000))
