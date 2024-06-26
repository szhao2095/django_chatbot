import json
import os
import hashlib
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

def compute_file_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def get_valid_file_paths(file_paths, loaded_files):
    valid_file_paths = []
    new_loaded_files = {}

    logger.debug("Starting file validation process.")
    logger.debug(f"Total files found: {len(file_paths)}")
    for path in file_paths:
        filename = os.path.basename(path)
        file_type = get_file_type(filename)
        file_hash = compute_file_hash(path)
        logger.debug(f"Checking file {filename} of type {file_type} with hash {file_hash}")

        if filename in loaded_files:
            if loaded_files[filename]['filehash'] == file_hash:
                logger.debug(f"File {filename} is already loaded and unchanged.")
                continue
            else:
                logger.debug(f"File {filename} is already loaded but has changed.")

        if file_type in ['doc', 'docx', 'pdf', 'txt']:
            valid_file_paths.append(path)
            new_loaded_files[filename] = {'filename': filename, 'filetype': file_type, 'filehash': file_hash}
            logger.debug(f"Including file {filename} with type {file_type} and hash {file_hash}.")
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

def delete_file_from_vector_store(client, vector_store_id, file_id):
    client.beta.vector_stores.files.delete(vector_store_id=vector_store_id, file_id=file_id)

def delete_file(client, file_id):
    client.files.delete(file_id)

def main():
    logger.debug("Initializing OpenAI client.")
    client = OpenAI(api_key=OPENAI_API_KEY)
    config = load_config()

    now = datetime.now(timezone.utc)

    if 'current_vector_store' not in config:
        config['current_vector_store'] = {}

    for desired_store in config.get('desired_vector_store', []):
        human_readable_id = desired_store['id']
        current_store = config['current_vector_store'].get(human_readable_id, {})
        vector_store_id = current_store.get('vector_store_id')
        last_creation_date_str = current_store.get('last_creation_date')
        last_creation_date = datetime.fromisoformat(last_creation_date_str).replace(tzinfo=timezone.utc) if last_creation_date_str else None

        recreate_vector_store = (
            not vector_store_id or 
            is_config_different(current_store, desired_store) or 
            (last_creation_date and (now - last_creation_date) > timedelta(weeks=1))
        )

        files_folder = os.path.join(os.path.dirname(__file__), desired_store['files_folder'])
        if not os.path.exists(files_folder):
            os.makedirs(files_folder)
        file_paths = get_file_paths(files_folder)
        file_names = [os.path.basename(path) for path in file_paths]
        loaded_files = {f['filename']: f for f in current_store.get('loaded_files', [])}

        if recreate_vector_store:
            logger.debug(f"Creating or updating the vector store with id: {human_readable_id}.")

            expires_after_anchor = desired_store.get("expires_after_anchor", "last_active_at")
            expires_after_days = desired_store.get("expires_after_days", 7)

            vector_store = client.beta.vector_stores.create(
                name=desired_store['vector_store_name'],
                expires_after={
                    "anchor": expires_after_anchor,
                    "days": expires_after_days
                }
            )
            vector_store_id = vector_store.id
            current_store['vector_store_id'] = vector_store_id
            current_store['expires_after_anchor'] = expires_after_anchor
            current_store['expires_after_days'] = expires_after_days

            valid_file_paths, new_loaded_files = get_valid_file_paths(file_paths, {})
            if valid_file_paths:
                upload_files(client, vector_store_id, valid_file_paths)
                current_store['loaded_files'] = list(new_loaded_files.values())

            current_store['vector_store_name'] = desired_store['vector_store_name']
            current_store['files_folder'] = desired_store['files_folder']
            current_store['last_creation_date'] = now.isoformat()
        else:
            logger.debug(f"Checking for new files to upload for vector store with id: {human_readable_id}.")
            vector_store_files = get_all_vector_store_files(client, vector_store_id)
            vector_store_file_ids = {file[1].filename: file[0].id for file in vector_store_files}
            valid_file_paths, new_loaded_files = get_valid_file_paths(file_paths, loaded_files)

            # Check for files to delete
            files_to_delete = []
            for filename, file_info in loaded_files.items():
                if filename not in new_loaded_files and filename not in file_names:
                    logger.debug(f"File {filename} is in loaded_files but not in directory, deleting from vector store and OpenAI files.")
                    delete_file_from_vector_store(client, vector_store_id, vector_store_file_ids[filename])
                    delete_file(client, vector_store_file_ids[filename])
                    files_to_delete.append(filename)

            for filename in files_to_delete:
                del loaded_files[filename]

            # Check for changed files
            for filename, file_info in new_loaded_files.items():
                if filename in loaded_files and loaded_files[filename]['filehash'] != file_info['filehash']:
                    logger.debug(f"File {filename} has changed, deleting old version from vector store and OpenAI files.")
                    delete_file_from_vector_store(client, vector_store_id, vector_store_file_ids[filename])
                    delete_file(client, vector_store_file_ids[filename])

            if valid_file_paths:
                upload_files(client, vector_store_id, valid_file_paths)
                loaded_files.update(new_loaded_files)

            current_store['loaded_files'] = list(loaded_files.values())

        config['current_vector_store'][human_readable_id] = current_store

    config['last_run_date'] = now.isoformat()
    save_config(config)
