from ast import parse
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import json
from logparser.clf_parser import clf_parser
from logparser.json_parser import json_parser
from logparser.hadoop_parser import hadoop_parser, is_hadoop_log_file
from logparser.zookeeper_parser import zookeeper_parser, is_zookeeper_log_file
from logparser.hdfs_parser import hdfs_parser, is_hdfs_log_file

app = Flask(__name__)
CORS(app)

uploaded_files = []

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'log', 'syslog', 'json'}

OUTPUT_FOLDER = 'parsed_logs'
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB maximum file size

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

parsed_file_name = ''

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        parsed_file_name = file.filename
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        # Read the content of the file
        file_content = file.read()
        # print(file_content)

        # Create the uploads folder if it doesn't exist
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        # Save the file to the uploads folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        with open(file_path, 'wb') as uploaded_file:
            uploaded_file.write(file_content)
        
        # Create the output folder for the storing parsed json file.
        if not os.path.exists(app.config['OUTPUT_FOLDER']):
            os.makedirs(app.config['OUTPUT_FOLDER'])

        uploaded_files.append(file.filename)
        file_extension = file.filename.split('.')[-1]
        handle_uploaded_file(file_path, file_extension)
        return jsonify({'message': 'File uploaded successfully'}), 200

    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.route('/receive', methods=['POST'])
def receive_data():
    try:
        data = request.get_json()
        print("Received data:", data)
        # Add your processing logic here
        return jsonify({"status": "success"})
    except Exception as e:
        print("Error processing data:", str(e))
        return jsonify({"status": "error", "message": str(e)})


@app.route('/get_parsed_log_file_path', methods=['GET'])
def get_parsed_log_file_path():
    
    # logs_file_path = os.path.join('parsed_logs', parsed_file_name)  # Replace with the actual path to your file
    # if os.path.exists(logs_file_path):
    with open('parsed_logs/output.json', 'r') as file:
        logs_content = file.read()
        
        # return jsonify(logs_content)
        return logs_content
    # else:
    #     return jsonify({"error": "File not found"}), 404


def handle_uploaded_file(file_path, file_extension):
    parsed_file = None
    if file_extension == 'json':
        json_parser(file_path, app.config['OUTPUT_FOLDER'])
    elif file_extension == 'log':
        if is_hadoop_log_file(file_path):
            hadoop_parser(file_path, app.config['OUTPUT_FOLDER'])
        elif is_zookeeper_log_file(file_path):
            zookeeper_parser(file_path, app.config['OUTPUT_FOLDER'])
        elif is_hdfs_log_file(file_path):
            hdfs_parser(file_path, app.config['OUTPUT_FOLDER'])
        else:
            clf_parser(file_path, app.config['OUTPUT_FOLDER'])


if __name__ == '__main__':
    app.run(debug=True)
