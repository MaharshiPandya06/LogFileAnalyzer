from datetime import datetime
import re
import json

log_entry_pattern = re.compile(r'^(\d{6} \d{6}) (\d+) (\w+) (.+)$')

def is_hdfs_log_file(input_file_path):
    try:
        with open(input_file_path, "r") as file:
            for line in file:
                # Parse the log entry
                return bool(log_entry_pattern.match(line.strip()))

    except FileNotFoundError:
        print(f"File '{input_file_path}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def parse_hdfs_log(log_entry):
    match = log_entry_pattern.match(log_entry)

    if match:
        unformatted_date_time = match.group(1)
        log_level = match.group(3)
        message = match.group(4)

        formatted_date_time = datetime.strptime(unformatted_date_time, "%y%m%d %H%M%S").strftime("%Y-%m-%d %H:%M:%S")

        return {
            "timestamp": formatted_date_time,
            "log_level": log_level,
            "message": message,
        }
    else:
        print(f"Failed to match log entry: {log_entry}")
        return None

def hdfs_parser(input_file_path, output_file_path):
    parsed_data_list = []

    try:
        with open(input_file_path, "r") as file:
            # Read each line from the log file
            for line in file:
                # Parse the log entry
                parsed_data = parse_hdfs_log(line.strip())
                
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
