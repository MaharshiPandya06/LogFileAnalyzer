import json
import re
from datetime import datetime
import os
"""
This function parses the log and extracts timestamp, log level and the message from the log.
"""
def parse_json_log(log_entry):
    # Timstamp pattern with time zone offset 0
    timestamp_pattern_with_offset_0 = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z)?')
    # Timstamp pattern without time zone offset
    timestamp_pattern_without_offset = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(\.\d{3})?')
    # Log level pattern for finding log level in values.
    log_level_pattern = re.compile(r'(INFO|Info|info|DEBUG|Debug|debug|ERROR|Error|error|WARNING|Warning|warning|WARN|Warn|warn)')

    parsed_log = {
        "timestamp": None,
        "log_level": None,
        "message": None,
    } 

    for key, value in log_entry.items():
        if isinstance(value, str):
            if timestamp_pattern_with_offset_0.match(value) or timestamp_pattern_without_offset.match(value):
                # print(f"{key}, {value}")
                # parsed_log["timestamp"] = datetime.fromisoformat(value)
                parsed_log["timestamp"] = value
            elif log_level_pattern.match(value):
                parsed_log["log_level"] = value
            elif key == 'message' or key == 'content' or key == 'description':
                # print(f"key is {key}")
                parsed_log["message"] = value
            else:
                if not parsed_log["message"]:
                    parsed_log["not_message"] = value

    return parsed_log

"""
This function converts serializes the timestamp
"""
def datetime_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")

def json_parser(input_file_path, output_file_path):
    # Path to your JSON log file
    # log_file_path = 'sample_log.json'
    # log_file_path = input_file_path
    # # Output JSON file path
    # # output_json_file_path = './output/output.json'
    # output_json_file_path = output_file_path

    parsed_logs = []

    # try:
    #     with open(log_file_path, 'r') as file:
    #         logs = json.load(file)
            
    #         count = 0
    #         for log_entry in logs:
    #             count += 1
    #             parsed_logs.append(parse_json_log(log_entry))
    #         print(count) 
    #     with open(output_json_file_path, 'w') as output_file:
    #         json.dump(parsed_logs, output_file, indent=2, default=datetime_serializer)
    #         print(f"Parsed logs saved to {output_json_file_path}")

    # except FileNotFoundError:
    #     print(f"File '{log_file_path}' not found.")
    # except json.JSONDecodeError as e:
    #     print(f"Error decoding JSON: {e}")
    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}")

    try:
        with open(input_file_path, 'r') as file:
            logs = json.load(file)
            for log_entry in logs:
                parsed_logs.append(parse_json_log(log_entry))

        with open(output_file_path+"/output.json", 'w') as output_file:
            json.dump(parsed_logs, output_file, indent=2, default=datetime_serializer)
            print(f"Parsed logs saved to {output_file_path}")

    except FileNotFoundError:
        print(f"File '{input_file_path}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
