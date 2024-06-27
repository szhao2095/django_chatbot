import json
import os
from datetime import datetime, timedelta, timezone
from django.conf import settings
from openai import OpenAI

from .env_vars import OPENAI_API_KEY
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'assistant_config.json')

import logging
logger = logging.getLogger('chatbot_core')

def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            logger.debug("Loading configuration file.")
            return json.load(f)
    except FileNotFoundError:
        logger.debug("Configuration file not found.")
        return {}

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        logger.debug("Saving configuration file.")
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
    config = load_config()

    now = datetime.now(timezone.utc)

    assistant_id = config.get('assistant_id')
    last_creation_date_str = config.get('last_creation_date')
    last_creation_date = datetime.fromisoformat(last_creation_date_str).replace(tzinfo=timezone.utc) if last_creation_date_str else None

    if (
        not assistant_id or 
        is_config_different(config['current_assistant'], config['desired_assistant']) or 
        (last_creation_date and (now - last_creation_date) > timedelta(weeks=1))
    ):
        logger.debug("Creating or updating the assistant.")
        assistant = client.beta.assistants.create(
            name=config['desired_assistant']['name'],
            description=config['desired_assistant']['description'],
            model=config['desired_assistant']['model'],
            tools=config['desired_assistant']['tools']
        )
        config['assistant_id'] = assistant.id
        config['current_assistant'] = config['desired_assistant']
        config['last_creation_date'] = now.isoformat()

    config['last_run_date'] = now.isoformat()
    save_config(config)