from telegram.ext import MessageHandler, filters
from .base_handler import BaseHandler
class TextHandler(BaseHandler):
    def __init__(self, function):
        self.function = function

    def register(self, app):
        app.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, 
                self.function
            )
        )