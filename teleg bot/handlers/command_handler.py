
from telegram.ext import CommandHandler as TelegramCommandHandler
from .base_handler import BaseHandler


class CommandHandler(BaseHandler):

    def __init__(self, handlers):
        self.handlers = handlers

    def register(self, app):
        for command, function in self.handlers.items():
            app.add_handler(
                TelegramCommandHandler(command, function)
            )