import time
import schedule
import functools
import traceback
from src.notifier import Notifier
from src.utils.logger import logger
from src.utils.configurer import config
from requests.exceptions import ConnectionError
from src.telegram_notifier import TelegramNotifier


def get_channels():
    telegram_status = config.get_configuration('status', "TELEGRAM", is_boolean=True)
    if telegram_status:
        telegram_n = TelegramNotifier(config.get_configuration('token', "TELEGRAM"))
    else:
        telegram_n = None
    os_status = config.get_configuration('status', "OS", is_boolean=True)
    if os_status:
        from plyer import notification
    else:
        notification = None
    return telegram_n, notification


def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except IndexError:
                logger.log("critical", "Need to run login.py script since session is either outdated or never created.")
            except ConnectionError:
                logger.log("critical", "BigBasket didn't respond well.")
            except:
                logger.log("critical", traceback.format_exc())
                logger.log("critical", "Please report the developer at "
                                       "https://github.com/wrap-away/bigbasket-notifier/issues "
                                       "to inform him about this error.")
            if cancel_on_failure:
                logger.log("warning", "Job Cancelled due to an error.")
                return schedule.CancelJob
        return wrapper
    return catch_exceptions_decorator


@catch_exceptions(cancel_on_failure=False)
def job(notifier: Notifier, delay: int, system_notifier, telegram_notifier):
    """
    Job to check if a delivery slot gets available for the default selected address in your bigbasket website.
    @param notifier: Notifier - Notifier class - To monitor bigbasket website.
    @param system_notifier: None/notification class - To notify users (cross-platform) via balloon tiles.
    @param delay: int - Just a preventive measure to not make too many requests at the same time.
    @param telegram_notifier: None/Bot class - Telegram integration to notify via bot.
    """
    notifier.visit_main_page()
    time.sleep(delay)
    addr_id = notifier.visit_cart_page_and_get_address_id()
    time.sleep(delay)
    initial_status, resp = notifier.check_if_delivery_slot_available(addr_id)
    if not initial_status:
        return None
    logger.log("warning", "Maybe a delivery slot is found.")
    time.sleep(delay)
    status = notifier.visit_extra_delivery_slot_check()
    if not status:
        logger.log("warning", "No delivery slot was found.")
        return None
    success_message = "A free delivery slot is found for your address!"
    logger.log("critical", success_message)
    if system_notifier:
        system_notifier.notify(
            title='BigBasket Notifier',
            message=success_message,
            app_name='bigbasket-notifier'
        )
    if telegram_notifier:
        telegram_notifier.notify(config.get_configuration('chat_id', "TELEGRAM"), success_message)
    return None


if __name__ == "__main__":
    n = Notifier(
        config.get_configuration('phone_number', "APP"),
        config.get_configuration('session_pickle_filename', "SYSTEM"),
        load_session=True,
        debug=config.get_configuration('debug', "DEV")
    )
    telegram, system_notification = get_channels()
    job(n, 2, system_notification, telegram)
    schedule.every(
        int(config.get_configuration("interval", "APP"))
    ).minutes.do(job, n, 2, system_notification, telegram)
    while True:
        schedule.run_pending()
        time.sleep(1)
