from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
import pandas as pd
import matplotlib
from io import BytesIO
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Image,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import ParagraphStyle
from logparser.clf_parser import clf_parser
from logparser.json_parser import json_parser
from logparser.hadoop_parser import hadoop_parser, is_hadoop_log_file
from logparser.zookeeper_parser import zookeeper_parser, is_zookeeper_log_file
from logparser.hdfs_parser import hdfs_parser, is_hdfs_log_file

matplotlib.use('Agg')
import matplotlib.pyplot as plt

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
    """
    Check if the provided filename is allowed.

    Parameters:
    - filename (str): The name of the file to be checked.

    Returns:
    bool: True if the file extension is allowed, False otherwise.

    Example:
    >>> allowed_file('example.log')
    True
    >>> allowed_file('document.txt')
    False
    """
    return (
        '.' in filename and filename.rsplit('.', 1)[1].lower() in (
            ALLOWED_EXTENSIONS
        )
    )


def handle_uploaded_file(file_path, file_extension):
    """
    Send the uploaded file to appropriate parser based on its extension.

    Parameters:
    - file_path (str): The path to the uploaded file.
    - file_extension (str): The extension of the uploaded file.

    Returns:
    None

    Notes:
    - If the file extension is 'json', it is parsed using the json_parser function.
    - If the file extension is 'log', the appropriate parser is chosen based on
    the log type.
      - Hadoop logs are parsed using hadoop_parser.
      - Zookeeper logs are parsed using zookeeper_parser.
      - HDFS logs are parsed using hdfs_parser.
      - Other logs are parsed using clf_parser.
    """
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


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handles file uploads via a POST request and sends it for file handling.

    Endpoint: /upload
    Methods: POST

    Returns:
        JSON: A JSON response indicating the status of the file upload.

    Responses:
        - 200 OK: File uploaded successfully.
        - 400 Bad Request: If no file is provided, the selected file is
        empty, or the file type is not allowed.
        - 500 Internal Server Error: If an unexpected server error occurs
        during file processing.

    Notes:
        - Allowed file types are determined by the `allowed_file` function.
        - The uploaded file gets saved to the 'uploads' folder.
        - The corresponding parsed JSON file is stored in the 'output' folder.

    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        # Read the content of the file
        file_content = file.read()

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


@app.route('/get_parsed_log_file_path', methods=['GET'])
def get_parsed_log_file_path():
    """
    Retrieve the content of the parsed log file from parsed folder.

    Endpoint: /get_parsed_log_file_path
    Method: GET

    Returns:
        str: The content of the parsed log file in JSON format.

    Notes:
        - The endpoint returns the content of the parsed log file stored in 
        'parsed_logs/output.json'.
        - The content is returned as a JSON string.
        - If the file is not found, a 404 error is returned.

    """
    try:
        with open('parsed_logs/output.json', 'r') as file:
            logs_content = file.read()
        return logs_content
    except FileNotFoundError:
        return jsonify({"error": "Parsed log file not found"}), 404


@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    """
    Generate a PDF report based on filtered log data.

    Endpoint: /generate_pdf
    Method: POST

    Parameters:
        - start_timestamp (str): Start timestamp for log filtering.
        - end_timestamp (str): End timestamp for log filtering.

    Returns:
        Response: A PDF file containing a line chart and a table containing
        log data.

    Responses:
        - 200 OK: Successful PDF generation.
        - 400 Bad Request: If required parameters are missing or invalid.
        - 500 Internal Server Error: If an unexpected server error occurs 
        during PDF generation.

    Notes:
        - Requires a JSON payload with start_timestamp and end_timestamp for
        log filtering.
        - Retrieves log data from 'parsed_logs/output.json'.
        - Generates a line chart and a table based on the filtered log data.
        - Returns a PDF file as an attachment named 'logs_report.pdf'.
    """
    # Convert start and end timestamp to appropriate datetime object.
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

    # Read the parsed json file and convert it to a dataframe
    logs_df = pd.read_json('parsed_logs/output.json')
    # Sort the dataframe entries in ascending order as per the timestamp column
    logs_df.sort_values(by='timestamp', inplace=True)
    # Convert the timestamp column in the dataframe to ISO 8601 format
    logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], format='ISO8601')
    filtered_logs = logs_df

    # Filter the logs based on the start and the end timestamps
    if start_timestamp and end_timestamp:
        filtered_logs = logs_df[(logs_df['timestamp'] >= start_timestamp) & (logs_df['timestamp'] <= end_timestamp)]
    elif start_timestamp and not end_timestamp:
        filtered_logs = logs_df[(logs_df['timestamp'] >= start_timestamp)]
    elif not start_timestamp and end_timestamp:
        filtered_logs = logs_df[(logs_df['timestamp'] <= end_timestamp)]

    # Plot a line chart
    line_chart_buffer = BytesIO()
    plt.figure(figsize=(12, 9))
    plt.plot(filtered_logs['timestamp'], filtered_logs['log_level'], marker='o')
    plt.xlabel('Timestamp')
    plt.ylabel('Log Level')
    plt.title('Line Chart')
    plt.xticks(rotation=45, ha='right')
    plt.savefig(line_chart_buffer, format='png')
    plt.close()

    # Create a paragraph style for log messages so that they stay wrapped.
    normal_style = ParagraphStyle(
        'Normal',
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.black,
        # Enable word wrapping for CJK languages (Chinese, Japanese, Korean)
        wordWrap='CJK',
    )
    # Apply this paragraph style to all the log messages in the filtered dataframe
    messages = [Paragraph(text, style=normal_style) for text in filtered_logs['message']]
    # Arrange the table data from the filtered dataframe
    table_data = [filtered_logs.columns] + list(
        zip(filtered_logs['timestamp'], filtered_logs['log_level'], messages))

    # Prepare a pdf with the line chart and the table created above.
    pdf_buffer = BytesIO()
    pdf = SimpleDocTemplate(pdf_buffer, pagesize=(800, 700))

    pdf_buffer.seek(0)

    col_widths = [150, 80, 300]
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

    dummy_space = Spacer(1, 20)

    line_chart_buffer.seek(0)
    line_chart_image = Image(line_chart_buffer, width=400, height=300)
    pdf.build([line_chart_image, dummy_space, table])

    pdf_bytes = pdf_buffer.getvalue()

    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=logs_report.pdf'

    return response


if __name__ == '__main__':
    app.run(debug=True)
