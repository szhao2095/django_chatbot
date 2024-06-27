import json
import os
from datetime import datetime, timedelta, timezone
from openai import OpenAI

from .env_vars import OPENAI_API_KEY
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'vector_store_config.json')

import logging
logger = logging.getLogger('chatbot_core')

def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            logger.debug("Loading vector store configuration file.")
            return json.load(f)
    except FileNotFoundError:
        logger.debug("Vector store configuration file not found.")
        return {}

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        logger.debug("Saving vector store configuration file.")
        json.dump(config, f, indent=4)

def is_config_different(current, desired):
    return (
        current['vector_store_name'] != desired['vector_store_name'] or
        current['files_folder'] != desired['files_folder']
    )

def get_file_paths(folder):
    return [os.path.join(folder, filename) for filename in os.listdir(folder) if os.path.isfile(os.path.join(folder, filename))]

def get_file_type(filename):
    return os.path.splitext(filename)[1][1:]

def get_valid_file_paths(file_paths, loaded_filenames):
    valid_file_paths = []
    new_loaded_files = []

    logger.debug("Starting file validation process.")
    logger.debug(f"Total files found: {len(file_paths)}")
    for path in file_paths:
        filename = os.path.basename(path)
        filename = os.path.basename(path)
        file_type = get_file_type(filename)
        logger.debug(f"Checking file {filename} of type {file_type}")

        if filename in loaded_filenames:
            logger.debug(f"File {filename} is already loaded.")
            continue
            
        if file_type in ['doc', 'docx', 'pdf', 'txt']:
            valid_file_paths.append(path)
            new_loaded_files.append({'filename': filename, 'filetype': file_type})
            logger.debug(f"Including file {filename} with type {file_type}.")
        else:
            logger.debug(f"Skipping file {filename} with unsupported file type {file_type}.")

    return valid_file_paths, new_loaded_files

def upload_files(client, vector_store_id, valid_file_paths):
    file_streams = [open(path, "rb") for path in valid_file_paths]
    try:
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store_id, files=file_streams
        )
        logger.debug(f"After upload: {file_batch.status} {file_batch.file_counts} ")
    finally:
        for file in file_streams:
            file.close()

def get_all_vector_store_files(client, vector_store_id):
    vector_store = client.beta.vector_stores.retrieve(vector_store_id)
    file_list = client.beta.vector_stores.files.list(vector_store_id=vector_store.id)
    all_files = []
    for file in file_list.data:
        file_details = client.files.retrieve(file.id)
        all_files.append((file, file_details))
        print(f"File ID: {file.id}, Filename: {file_details.filename}")

    return all_files

def main():
    logger.debug("Initializing OpenAI client.")
    client = OpenAI(api_key=OPENAI_API_KEY)
    config = load_config()

    now = datetime.now(timezone.utc)

    vector_store_id = config.get('vector_store_id')
    last_creation_date_str = config.get('last_creation_date')
    last_creation_date = datetime.fromisoformat(last_creation_date_str).replace(tzinfo=timezone.utc) if last_creation_date_str else None

    recreate_vector_store = (
        not vector_store_id or 
        is_config_different(config['current_vector_store'], config['desired_vector_store']) or 
        (last_creation_date and (now - last_creation_date) > timedelta(weeks=1))
    )

    files_folder = os.path.join(os.path.dirname(__file__), config['desired_vector_store']['files_folder'])
    if not os.path.exists(files_folder):
        os.makedirs(files_folder)
    file_paths = get_file_paths(files_folder)
    loaded_filenames = {file_info['filename'] for file_info in config['loaded_files']}

    if recreate_vector_store:
        logger.debug("Creating or updating the vector store.")
        vector_store = client.beta.vector_stores.create(
            name=config['desired_vector_store']['vector_store_name'],
            expires_after={
              "anchor": "last_active_at",
              "days": 7
            }
        )
        vector_store_id = vector_store.id
        config['vector_store_id'] = vector_store_id

        valid_file_paths, new_loaded_files = get_valid_file_paths(file_paths, set())
        if valid_file_paths:
            upload_files(client, vector_store_id, valid_file_paths)
            config['loaded_files'] = new_loaded_files

        config['current_vector_store'] = config['desired_vector_store']
        config['last_creation_date'] = now.isoformat()
    else:
        logger.debug("Checking for new files to upload.")
        valid_file_paths, new_loaded_files = get_valid_file_paths(file_paths, loaded_filenames)

        if valid_file_paths:
            upload_files(client, vector_store_id, valid_file_paths)
            config['loaded_files'].extend(new_loaded_files)

    config['last_run_date'] = now.isoformat()
    save_config(config)
