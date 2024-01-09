from datetime import datetime
import re
import json

log_entry_pattern = re.compile(r'(\S+) - - \[([^\]]+)\] "(\S+ .*?)" (\d+) (\d+)')

# log_entry_pattern = re.compile(r'(\S+) (-|\w+) (-|\w+) \[([^\]]+)\] "(\S+ .*?)" (\d+) (\d+)')
def is_clf_log_entry(log_entry):
    return bool(log_entry_pattern.match(log_entry))

def parse_clf_log(log_entry):
    match = log_entry_pattern.match(log_entry)

    if match:
        ip_address = match.group(1)
        timestamp = match.group(2)
        request = match.group(3)
        status_code = int(match.group(4))
        size = int(match.group(5))
        log_level = ''
        if status_code >= 200 and status_code <= 299:
            log_level = 'INFO'
        elif status_code >= 300 and status_code <= 399:
            log_level = 'WARN'
        else:
            log_level = 'ERROR'
        return {
            "ip_address": ip_address,
            "timestamp": convert_to_iso_format(timestamp),
            "message": request,
            "log_level": log_level,
            "size": size
        }
    else:
        print(f"Failed to match log entry: {log_entry}")
        return None

def convert_to_iso_format(timestamp):
    # Parse the timestamp using the format
    timestamp_datetime = datetime.strptime(timestamp, "%d/%b/%Y:%H:%M:%S %z")

    # Convert to ISO format
    iso_format = timestamp_datetime.isoformat()

    return iso_format

def clf_parser(input_file_path, output_file_path):

    parsed_data_list = []

    try:
        with open(input_file_path, "r") as file:
            # Read each line from the log file
            for line in file:
                # Parse the log entry
                parsed_data = parse_clf_log(line.strip())
                
                if parsed_data:
                    parsed_data_list.append(parsed_data)

        # Save the parsed data to a JSON file
        with open(output_file_path + '/output.json', "w") as json_file:
            json.dump(parsed_data_list, json_file, indent=2)

    except FileNotFoundError:
        print(f"File '{input_file_path}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")