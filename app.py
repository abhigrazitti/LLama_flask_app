from flask import Flask, render_template, request, jsonify
#from langchain_llama2 import llama2_main_function
from langchain_llama2_custom import llama2_main_function
import os

app = Flask(__name__)

# Define the allowed file extensions
ALLOWED_EXTENSIONS = {'txt'}

# Define a folder to store uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file_api():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"})

    if file and file.filename.endswith('.txt'):
        # Save the uploaded file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # You can add your processing logic here
        result = llama2_main_function(file_path)
        print("printing result.............")
        print(result)

        return jsonify({"message": result})

    else:
        return jsonify({"error": "Invalid file format. Please upload a .txt file"})



@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file"
    
    if file and file.filename.endswith('.txt'):
        # Save the uploaded file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # You can add your processing logic here
        result = llama2_main_function(file_path)
        print("printing result.............")
        print(result)

        return render_template('index.html', content=result)
        
    else:
        return "Invalid file format. Please upload a .txt file."


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
