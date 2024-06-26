import time
from openai import OpenAI
from .env_vars import OPENAI_API_KEY

from typing_extensions import override
from openai import AssistantEventHandler

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
        assistant_id=None, 
        thread_id=None,
        vector_store_id=None,
        streamOutput=True,
        eventHandler=EventHandler()
    ):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

        self.streamOutput = streamOutput

        if not assistant_id:
            assistant_id = self.client.beta.assistants.create(
                name="Tax Assistant",
                description="You are a tax assistant. Assist with tax related questions.",
                model="gpt-4o",
                tools=[{"type": "file_search"}]
            ).id
        self.assistant_id = assistant_id

        if not thread_id:
            thread_id = self.client.beta.threads.create().id
        self.thread_id = thread_id

        if not vector_store_id:
            vector_store_id = self.client.beta.vector_stores.create(name="Vector Store").id
        self.vector_store_id = vector_store_id


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
              print(f"Assistant: {last_message.content[0].text.value}")


# import logging
# from langchain_openai import ChatOpenAI
# from langchain.memory import ConversationSummaryBufferMemory
# from langchain.chains import ConversationChain
# from concurrent.futures import ThreadPoolExecutor
# from .env_vars import OPENAI_API_KEY, CLAUDE_API_KEY

# logger = logging.getLogger('chatbot_core')

# executor = ThreadPoolExecutor(max_workers=10)

# class ChatService:
#     def __init__(self, user_id, ai_provider='openai'):
#         self.user_id = user_id
#         self.conversation_history = []

#         self.ai_provider = ai_provider
#         self.setup_ai_provider()

#     def setup_ai_provider(self):
#         if self.ai_provider == 'openai':
#             logger.debug("Creating OpenAI provider")
#             self.llm = ChatOpenAI(
#                 api_key=OPENAI_API_KEY,
#                 model_name="gpt-3.5-turbo"
#             )
#             self.memory = ConversationSummaryBufferMemory(
#                 llm=self.llm,
#                 max_token_limit=650
#             )
#             self.conversation = ConversationChain(
#                 llm=self.llm,
#                 memory=self.memory
#             )
#         # Add other AI providers here

#     def handle_message(self, message):
#         response = self.call_ai_provider(message)
#         self.conversation_history.append((message, response))
#         # Save the message and response in a background thread
#         self.save_to_database(message, response)
#         return response

#     def call_ai_provider(self, message):
#         logger.debug("Calling AI provider")
#         try:
#             response = self.conversation.invoke(message)
#             logger.debug(f"AI response: {response}")
#             return response
#         except Exception as e:
#             logger.error(f"Error calling AI provider: {e}")
#             return "An error occurred while processing your request."

#     def save_to_database(self, message, response):
#         from .models import ChatHistory
#         def _save():
#             try:
#                 logger.debug(f"{self.user_id}: Saving to database: {message}, {response}")
#                 ChatHistory.objects.create(
#                     user_id=self.user_id,
#                     message=message,
#                     response=response
#                 )
#                 logger.debug("Message saved successfully")
#             except Exception as e:
#                 logger.error(f"Error saving chat history: {e}")
        
#         # Submit the save task to the executor
#         executor.submit(_save)
