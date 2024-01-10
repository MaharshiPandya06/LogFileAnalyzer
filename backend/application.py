from ast import parse
from operator import index
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
import requests
import os
import json
from logparser.clf_parser import clf_parser
from logparser.json_parser import json_parser
from logparser.hadoop_parser import hadoop_parser, is_hadoop_log_file
from logparser.zookeeper_parser import zookeeper_parser, is_zookeeper_log_file
from logparser.hdfs_parser import hdfs_parser, is_hdfs_log_file
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# from weasyprint import HTML
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle

app = Flask(__name__)
CORS(app)

uploaded_files = []

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'log', 'json'}

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

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    if request.json['start_timestamp'] == '' and request.json['end_timestamp'] == '':
        start_timestamp = None
        end_timestamp = None
    elif request.json['start_timestamp'] != '' and request.json['end_timestamp'] == '':
        start_timestamp = pd.to_datetime(request.json['start_timestamp'])
        end_timestamp = None
    elif request.json['start_timestamp'] == '' and request.json['end_timestamp'] != '':
        start_timestamp = None
        end_timestamp = pd.to_datetime(request.json['end_timestamp'])
    else:
        start_timestamp = pd.to_datetime(request.json['start_timestamp'])
        end_timestamp = pd.to_datetime(request.json['end_timestamp'])

    logs_df = pd.read_json('parsed_logs/output.json')
    logs_df.sort_values(by='timestamp', inplace=True)
    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], format='ISO8601')
    filtered_logs = logs_df
    
    if start_timestamp and end_timestamp:
        filtered_logs = logs_df[(logs_df['timestamp'] >= start_timestamp) & (logs_df['timestamp'] <= end_timestamp)]
    elif start_timestamp and not end_timestamp:
        filtered_logs = logs_df[(logs_df['timestamp'] >= start_timestamp)]
    elif not start_timestamp and end_timestamp:
        filtered_logs = logs_df[(logs_df['timestamp'] <= end_timestamp)]

    line_chart_buffer = BytesIO()
    plt.figure(figsize=(12,9))
    plt.plot(filtered_logs['timestamp'], filtered_logs['log_level'], marker='o')
    plt.xlabel('Timestamp')
    plt.ylabel('Log Level')
    plt.title('Line Chart')
    plt.xticks(rotation=45, ha='right')
    plt.savefig(line_chart_buffer, format='png')
    plt.close()
    normal_style = ParagraphStyle(
        'Normal',
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.black,
        wordWrap='CJK',  # Enable word wrapping for CJK languages (Chinese, Japanese, Korean)
    )
    messages = [Paragraph(text, style=normal_style) for text in filtered_logs['message']]

    table_data = [filtered_logs.columns] + list(zip(filtered_logs['timestamp'], filtered_logs['log_level'], messages))

    

    pdf_buffer = BytesIO()
    pdf = SimpleDocTemplate(pdf_buffer, pagesize=landscape(letter))

    pdf_buffer.seek(0)

    # image = Image(line_chart_path, width=400, height=200)
    # pdf.build([image])
    col_widths = [120, 80, 300]
    table = Table(table_data, colWidths=col_widths)
    style = TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ])
    table.setStyle(style)
    # pdf.build([table])
    
    dummy_space = Spacer(1, 20)

    line_chart_buffer.seek(0)
    line_chart_image = Image(line_chart_buffer, width=400, height=300)
    # pdf.build([line_chart_image] + [table])
    pdf.build([line_chart_image, dummy_space, table])

    pdf_bytes = pdf_buffer.getvalue()

    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=logs_report.pdf'

    return response

if __name__ == '__main__':
    app.run(debug=True)
