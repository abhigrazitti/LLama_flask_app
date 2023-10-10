from flask import Flask, render_template, request, jsonify
#from langchain_llama2 import llama2_main_function
from langchain_llama2_custom import llama2_main_function1, llama2_main_function2
import os
import re


def preprocess_transcript_file(file_path):
    
    if file_path.lower().endswith('.vtt'):
        with open(file_path, 'r') as file:
            text = file.read()
        # Removing timestamps and numbering using regular expressions
        cleaned_text = re.sub(r'\d+\n\d\d:\d\d:\d\d\.\d+ --> \d\d:\d\d:\d\d\.\d+\n', '', text)
        cleaned_text = re.sub(r'^WEBVTT\n', '', cleaned_text, flags=re.MULTILINE)

        # Removing extra spaces and empty lines
        cleaned_text = re.sub(r'\n+', '\n', cleaned_text)
        cleaned_text = cleaned_text.strip()

        # Save cleaned text to a .txt file
        output_file_path = os.path.splitext(file_path)[0] + '_cleaned.txt'
        with open(output_file_path, 'w') as output_file:
            output_file.write(cleaned_text)

        return output_file_path

    elif file_path.lower().endswith('.txt'):
        # If file name extension .txt file, return the content as it is
        return file_path

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


#frontend route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file"
    
    if file:
        # Save the uploaded file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        #preprocessing file
        file_path =  preprocess_transcript_file(file_path)
        

        # You can add your processing logic here
        result1 = llama2_main_function1(file_path)
        # result2 = llama2_main_function2(file_path)
        print("printing result1.............")
        print(result1)

        # print("printing result2.............")
        # print(result2)

        return render_template('index.html', content=result1)
        
    else:
        return "Invalid file format. Please upload a .txt file or .vtt"





#ignore only for api access
@app.route('/api/upload', methods=['POST'])
def upload_file_api():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"})

    if file:
        # Save the uploaded file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        #preprocessing file
        file_path =  preprocess_transcript_file(file_path)
        # file.save(file_path)

        # You can add your processing logic here
        result = llama2_main_function(file_path)
        print("printing result.............")
        print(result)

        return jsonify({"message": result})

    else:
        return jsonify({"error": "Invalid file format. Please upload a .txt file"})




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
