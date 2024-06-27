from django.apps import AppConfig

import logging
logger = logging.getLogger("chatbot_core")

class ChatbotCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatbot_core'

    def ready(self):
        from . import startup
        try:
            startup.main()
            logger.info("Assistant configuration checked and updated successfully.")
            logger.debug("Assistant configuration checked and updated successfully.")
        except Exception as e:
            logger.error(f"Error in assistant configuration script: {e}")