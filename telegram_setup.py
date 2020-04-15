import logging
import threading
from telegram.ext import Updater
from telegram.ext import CommandHandler
from src.utils.configurer import config


def shutdown():
    updater.stop()
    updater.is_idle = False


def start(update, context):
    chat_id = str(update.effective_chat.id)
    config.write_configuration('chat_id', chat_id, 'TELEGRAM')
    msg = "Successfully configured Telegram Channel! Your chat_id is: {0} which has been saved to config.ini".format(
        chat_id
    )
    print(msg)
    context.bot.send_message(chat_id=chat_id, text=msg)
    threading.Thread(target=shutdown).start()


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    print("Setting up telegram bot channel...")
    updater = Updater(token=config.get_configuration('token', "TELEGRAM"), use_context=True)
    start_handler = CommandHandler('start', start)
    updater.dispatcher.add_handler(start_handler)
    print("Send /start from your account to the newly created bot to finish the setup!")
    updater.start_polling()
