import logging
import openai
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationChain
from .models import ChatHistory
from .serializers import ChatHistorySerializer

from .env_vars import OPENAI_API_KEY, CLAUDE_API_KEY

logger = logging.getLogger('chatbot_core')

class ChatService:
    def __init__(self, user_id, message, ai_provider='openai'):
        self.user_id = user_id
        self.message = message
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

    def call_ai_provider(self):
        logger.debug("Calling AI provider")
        try:
            response = self.conversation.invoke(self.message)
            logger.debug(f"AI response: {response}")
            return response
        except Exception as e:
            logger.error(f"Error calling AI provider: {e}")
            return "An error occurred while processing your request."

    def save_to_database(self, response):
        logger.debug(f"Saving to database: {self.message}, {response}")
        try:
            chat_history = ChatHistory.objects.create(
                user_id=self.user_id,
                message=self.message,
                response=response,
            )
            logger.debug("Chat history saved successfully")
            return chat_history
        except Exception as e:
            logger.error(f"Error saving chat history: {e}")
            return None

    def get_reply(self):
        response = self.call_ai_provider()
        _ = self.save_to_database(response)
        return response
