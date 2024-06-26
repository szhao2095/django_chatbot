import logging
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationChain
from concurrent.futures import ThreadPoolExecutor
from .env_vars import OPENAI_API_KEY, CLAUDE_API_KEY

logger = logging.getLogger('chatbot_core')

executor = ThreadPoolExecutor(max_workers=10)

class ChatService:
    def __init__(self, user_id, ai_provider='openai'):
        self.user_id = user_id
        self.conversation_history = []

        self.ai_provider = ai_provider
        self.setup_ai_provider()

    def setup_ai_provider(self):
        if self.ai_provider == 'openai':
            logger.debug("Creating OpenAI provider")
            self.llm = ChatOpenAI(
                api_key=OPENAI_API_KEY,
                model_name="gpt-3.5-turbo"
            )
            self.memory = ConversationSummaryBufferMemory(
                llm=self.llm,
                max_token_limit=650
            )
            self.conversation = ConversationChain(
                llm=self.llm,
                memory=self.memory
            )
        # Add other AI providers here

    def handle_message(self, message):
        response = self.call_ai_provider(message)
        self.conversation_history.append((message, response))
        # Save the message and response in a background thread
        self.save_to_database(message, response)
        return response

    def call_ai_provider(self, message):
        logger.debug("Calling AI provider")
        try:
            response = self.conversation.invoke(message)
            logger.debug(f"AI response: {response}")
            return response
        except Exception as e:
            logger.error(f"Error calling AI provider: {e}")
            return "An error occurred while processing your request."

    def save_to_database(self, message, response):
        from .models import ChatHistory
        def _save():
            try:
                logger.debug(f"{self.user_id}: Saving to database: {message}, {response}")
                ChatHistory.objects.create(
                    user_id=self.user_id,
                    message=message,
                    response=response
                )
                logger.debug("Message saved successfully")
            except Exception as e:
                logger.error(f"Error saving chat history: {e}")
        
        # Submit the save task to the executor
        executor.submit(_save)
