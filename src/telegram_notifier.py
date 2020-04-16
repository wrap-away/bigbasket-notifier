from telegram.bot import Bot


class TelegramNotifier:
    def __init__(self, token):
        self.bot = Bot(token)

    def notify(self, chat_id, message):
        self.bot.send_message(chat_id, message)
