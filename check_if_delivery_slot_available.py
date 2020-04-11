import time
import schedule
from plyer import notification
from src.notifier import Notifier
from src.utils.configurer import config


def job(notifier: Notifier, system_notifier: notification, delay: int = 2):
    """
    Job to check if a delivery slot gets available for the default selected address in your bigbasket website.
    @param system_notifier: notification - To notify users (cross-platform) via balloon tiles.
    @param notifier: Notifier - Notifier class - To monitor bigbasket website.
    @param delay: int - Just a preventive measure to not make too many requests at the same time.
    """
    notifier.visit_main_page()
    time.sleep(delay)
    addr_id = notifier.visit_cart_page_and_get_address_id()
    time.sleep(delay)
    status, resp = notifier.check_if_delivery_slot_available(addr_id)
    if status:
        system_notifier.notify(
            title='BigBasket Notifier',
            message='A free delivery slot is found for your address',
            app_name='bigbasket-notifier'
        )


if __name__ == "__main__":
    n = Notifier(
        config.get_configuration('phone_number', "APP"),
        config.get_configuration('session_pickle_filename', "SYSTEM"),
        load_session=True
    )
    schedule.every(
        int(config.get_configuration("interval", "APP"))
    ).minutes.do(job, n, notification)
    while True:
        schedule.run_pending()
        time.sleep(1)
