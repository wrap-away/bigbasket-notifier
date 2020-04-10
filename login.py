import time
from src.notifier import Notifier
from src.utils.configurer import config

notifier = Notifier(
    config.get_configuration('phone_number', "APP"),
    config.get_configuration('session_pickle_filename', "SYSTEM")
)

notifier.visit_main_page()
time.sleep(2)  # Just a preventive measure to not make too many requests at the same time.
notifier.send_otp()
print("Enter your OTP")
otp = input()
notifier.login(otp)
notifier.save_session()
print("Session saved successfully!")
