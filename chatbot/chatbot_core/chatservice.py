import time
import os
import json
from openai import OpenAI
from .env_vars import OPENAI_API_KEY

from typing_extensions import override
from openai import AssistantEventHandler

import logging
logger = logging.getLogger('chatbot_core')

def load_config(config_path):
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    
ASSISTANT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'assistant_config.json')
VECTOR_STORE_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'vector_store_config.json')

class NewChatInitializer:
    def __init__(self, assistant_name):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.thread_id = self.client.beta.threads.create().id

        self.assistant_config = load_config(ASSISTANT_CONFIG_PATH)
        self.vector_store_config = load_config(VECTOR_STORE_CONFIG_PATH)
        
        self.current_assistant = self.assistant_config.get('current_assistants', {}).get(assistant_name)
        if not self.current_assistant:
            raise ValueError(f"Assistant with id {assistant_name} not found in current_assistants.")

        self.assistant_id = self.current_assistant.get('assistant_id')
        self.assistant_info = self.current_assistant

        self.vector_store_id = None
        self.vector_store_info = None

        if 'vector_store' in self.current_assistant and self.current_assistant['vector_store']:
            vector_store_name = self.current_assistant['vector_store']
            vector_store_info = self.vector_store_config.get('current_vector_store', {}).get(vector_store_name)
            if vector_store_info:
                self.vector_store_id = vector_store_info.get('vector_store_id')
                self.vector_store_info = vector_store_info


class EventHandler(AssistantEventHandler):    
    @override
    def on_text_created(self, text) -> None:
        print(f"Assistant: ", end="", flush=True)
        
    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)
        
    # def on_tool_call_created(self, tool_call):
    #   print(f"\nassistant > {tool_call.type}\n", flush=True)

    # def on_tool_call_delta(self, delta, snapshot):
    #   if delta.type == 'code_interpreter':
    #     if delta.code_interpreter.input:
    #       print(delta.code_interpreter.input, end="", flush=True)
    #     if delta.code_interpreter.outputs:
    #       print(f"\n\noutput >", flush=True)
    #       for output in delta.code_interpreter.outputs:
    #         if output.type == "logs":
    #           print(f"\n{output.logs}", flush=True)


class OpenAIChatService:
    def __init__(
        self, 
        thread_id,
        assistant_id,
        vector_store_id,
        streamOutput=False,
        eventHandler=EventHandler()
    ):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

        self.streamOutput = streamOutput

        self.thread_id = thread_id
        self.assistant_id = assistant_id
        self.vector_store_id = vector_store_id

        logger.debug(f"Created OpenAIChatService instance with thread_id:{self.thread_id}, assistant_id:{self.assistant_id}, vector_store_id:{self.vector_store_id}")


    def add_message(self, user_message, image_paths=None, file_paths=None):
        # Initialize message content with user message
        content = [{
            "type": "text",
            "text": user_message
        }]

        if image_paths:
            for image_path in image_paths:
                # Upload each image file
                file = self.client.files.create(
                    file=open(image_path, "rb"),
                    purpose="vision"
                )
                # Add image content to the message
                content.append(
                    {
                        "type": "image_file",
                        "image_file": {"file_id": file.id}
                    }
                )

        attachments = []
        if file_paths:
            for file_path in file_paths:
                # Upload each file
                file = self.client.files.create(
                    file=open(file_path, "rb"),
                    purpose="assistants"
                )
                # Add file to attachments
                attachments.append(
                    {
                        "file_id": file.id,
                        "tools": [{"type": "file_search"}]
                    }
                )

        # Add the message to the thread
        self.client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=content,
            attachments=attachments
        )


    def wait_on_run(self, run):
        while run.status in ["queued", "in_progress"]:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread_id,
                run_id=run.id
            )
            time.sleep(0.5)
        return run


    def get_response(self):
        # Retrieve and return all messages from the thread
        messages = self.client.beta.threads.messages.list(thread_id=self.thread_id)
        return messages.data


    def send_message(self, user_message, image_paths=None, file_paths=None):
        self.add_message(user_message, image_paths, file_paths)

        if self.streamOutput:
            with self.client.beta.threads.runs.stream(
                thread_id=self.thread_id,
                assistant_id=self.assistant_id,
                event_handler=self.EventHandler(),
            ) as stream:
                stream.until_done()
            print()
        else:
            run = self.client.beta.threads.runs.create(
                thread_id=self.thread_id,
                assistant_id=self.assistant_id,
            )
            run = self.wait_on_run(run)

            messages = self.get_response()
            last_message = next((message for message in messages if message.role == "assistant"), None)
            if last_message:
                msg = last_message.content[0].text.value
                print(f"Assistant: {msg}")
                return msg
        return None