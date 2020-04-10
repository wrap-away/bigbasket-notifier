import time
from src.notifier import Notifier
from src.utils.configurer import config

notifier = Notifier(
    config.get_configuration('phone_number', "APP"),
    config.get_configuration('session_pickle_filename', "SYSTEM"),
    load_session=True
)

notifier.visit_main_page()
time.sleep(2)  # Just a preventive measure to not make too many requests at the same time.
addr_id = notifier.visit_cart_page_and_get_address_id()
time.sleep(2)
status, resp = notifier.check_if_delivery_slot_available(addr_id)
