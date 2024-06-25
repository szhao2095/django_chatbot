# services.py
import openai
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory # https://www.pinecone.io/learn/series/langchain/langchain-conversational-memory/
from langchain.chains import ConversationChain
from .models import ChatHistory
from .serializers import ChatHistorySerializer

from .env_vars import OPENAI_API_KEY, CLAUDE_API_KEY

class ChatService:
    def __init__(self, user_id, message, ai_provider='openai'):
        self.user_id = user_id
        self.message = message
        self.ai_provider = ai_provider
        self.setup_ai_provider()

    def setup_ai_provider(self):
        if self.ai_provider == 'openai':
            print("Creating open ai ai provider")
            # openai.api_key = OPENAI_API_KEY
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
        print("Calling ai provider")
        response = self.conversation.invoke(self.message)
        return response

    def save_to_database(self, response):
        print("Saving to database: ", self.message, response)
        chat_history = ChatHistory.objects.create(
            user_id=self.user_id,
            message=self.message,
            response=response,
        )
        return chat_history

    def get_reply(self):
        response = self.call_ai_provider()
        _ = self.save_to_database(response)
        return response
