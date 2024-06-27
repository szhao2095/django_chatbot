import os
from django.apps import AppConfig

import logging
logger = logging.getLogger("chatbot_core")

class ChatbotCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatbot_core'

    def ready(self):
        if os.environ.get('RUN_MAIN') == 'true': 
            from . import assistant_startup
            try:
                logger.debug("==========================================================")
                assistant_startup.main()
                logger.info("Assistant configuration checked and updated successfully.")
                logger.debug("Assistant configuration checked and updated successfully.")
                logger.debug("==========================================================")
            except Exception as e:
                logger.error(f"Error in assistant configuration script: {e}")

            from . import vector_store_startup
            try:
                logger.debug("==========================================================")
                vector_store_startup.main()
                logger.info("Vector store configuration checked and updated successfully.")
                logger.debug("Vector store configuration checked and updated successfully.")
                logger.debug("==========================================================")
            except Exception as e:
                logger.error(f"Error in vector store configuration script: {e}")