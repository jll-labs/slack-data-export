import os
import json

def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            print(f"Directory created successfully: {directory_path}")
        except OSError as e:
            print(f"Error creating directory {directory_path}: {e}")
    else:
        print(f"Directory already exists: {directory_path}")

def store_file(file_data, file_id, file_name, channel_name):
    create_directory_if_not_exists(f'Output/{channel_name}/Attachments')
    with open(f'Output/{channel_name}/Attachments/{file_id}_{file_name}', 'wb') as file:
        file.write(file_data)

def store_raw_conversations_history(data, channel_name):
    with open(f'Output/{channel_name}/raw_conversations_history.json', 'w') as file:
        file.write(json.dumps(data))