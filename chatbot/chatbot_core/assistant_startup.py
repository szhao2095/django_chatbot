import json
import os
from datetime import datetime, timedelta, timezone
from openai import OpenAI

from .env_vars import OPENAI_API_KEY
ASSISTANT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'assistant_config.json')
VECTOR_STORE_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'vector_store_config.json')

import logging
logger = logging.getLogger('chatbot_core')

def load_config(path):
    try:
        with open(path, 'r') as f:
            logger.debug(f"Loading configuration file from {path}.")
            return json.load(f)
    except FileNotFoundError:
        logger.debug(f"Configuration file not found at {path}.")
        return {}

def save_config(config, path):
    with open(path, 'w') as f:
        logger.debug(f"Saving configuration file to {path}.")
        json.dump(config, f, indent=4)

def is_config_different(current, desired):
    return (
        current['name'] != desired['name'] or
        current['description'] != desired['description'] or
        current['model'] != desired['model'] or
        current['tools'] != desired['tools']
    )

def main():
    logger.debug("Initializing OpenAI client.")
    client = OpenAI(api_key=OPENAI_API_KEY)
    config = load_config(ASSISTANT_CONFIG_PATH)
    vector_store_config = load_config(VECTOR_STORE_CONFIG_PATH)

    now = datetime.now(timezone.utc)

    if 'current_assistants' not in config:
        config['current_assistants'] = {}

    for desired_assistant in config['desired_assistants']:
        human_readable_id = desired_assistant['id']
        current_assistant = config['current_assistants'].get(human_readable_id, {})
        assistant_id = current_assistant.get('assistant_id')
        last_creation_date_str = current_assistant.get('last_creation_date')
        last_creation_date = datetime.fromisoformat(last_creation_date_str).replace(tzinfo=timezone.utc) if last_creation_date_str else None

        if (
            not assistant_id or 
            is_config_different(current_assistant, desired_assistant) or 
            (last_creation_date and (now - last_creation_date) > timedelta(weeks=1))
            # or (vector_store_id and vector_store_id != current_assistant.get('vector_store_id'))
        ):
            logger.debug(f"Creating or updating the assistant with id: {human_readable_id}.")
            assistant = client.beta.assistants.create(
                name=desired_assistant['name'],
                description=desired_assistant['description'],
                model=desired_assistant['model'],
                tools=desired_assistant['tools']
            )
            assistant_id = assistant.id
            config['current_assistants'][human_readable_id] = {
                **desired_assistant,
                'assistant_id': assistant.id,
                'vector_store_id': "",
                'last_creation_date': now.isoformat()
            }

        # Check for vector store details
        if 'vector_store' in desired_assistant and desired_assistant['vector_store']:
            vector_store_id = vector_store_config['current_vector_store'].get(desired_assistant['vector_store'], {}).get('vector_store_id')

            if not vector_store_id:
                logger.debug(f"Vector store {desired_assistant['vector_store']} is specified for assistant {human_readable_id} but could not be found.")
            else:
                if vector_store_id != current_assistant.get('vector_store_id'):
                    logger.debug(f"Updating assistant {human_readable_id} with vector store id: {vector_store_id}.")
                    client.beta.assistants.update(
                        assistant_id=assistant_id,
                        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}}
                    )
                    config['current_assistants'][human_readable_id]['vector_store_id'] = vector_store_id

    config['last_run_date'] = now.isoformat()
    save_config(config, ASSISTANT_CONFIG_PATH)
