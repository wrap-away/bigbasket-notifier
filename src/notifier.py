import json
import pickle
import requests
from src.utils.logger import logger
from requests import Response, Session


class Notifier:
    BASE_URL = "https://www.bigbasket.com/"
    OTP_ENDPOINT = "mapi/v4.0.0/member-svc/otp/send/"
    LOGIN_ENDPOINT = "mapi/v4.0.0/member-svc/login/"
    CART_ENDPOINT = "basket/?ver=1"
    AVAILABILITY_ENDPOINT = "co/update-po/"

    def __init__(self, phone_number: str, session_pickle_filename: str, load_session: bool = False) -> None:
        logger.log("info", "Instantiating Notifier...")
        self.phone_number = phone_number
        self.session_pickle_filename = session_pickle_filename
        if load_session:
            self.session = self.load_session()
        else:
            self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/80.0.3987.163 Safari/537.36',
            'X-Channel': 'BB-WEB',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Caller': 'DVAR-SVC',
            'Sec-Fetch-Dest': 'empty',
            'Referer': self.BASE_URL
        }

    def visit_main_page(self) -> Response:
        logger.log("info", "Visiting main website...")
        resp = self.session.get(self.BASE_URL, headers=self.headers)
        if not resp.ok:
            logger.log("error", "Main page not reachable...")
            return resp
        self.headers['X-CSRFToken'] = resp.cookies.get('csrftoken')
        return resp

    def send_otp(self) -> Response:
        logger.log("info", "Sending OTP to {}...".format(self.phone_number))
        resp = self.session.post(self.BASE_URL + self.OTP_ENDPOINT, headers=self.headers, data=json.dumps(
            {
                "identifier": self.phone_number
            }
        ))
        if not resp.ok:
            logger.log("error", "Failed to send OTP.")
        return resp

    def login(self, otp: str) -> Response:
        logger.log("info", "Logging with OTP: {}...".format(otp))
        resp = self.session.post(self.BASE_URL + self.LOGIN_ENDPOINT, headers=self.headers, data=json.dumps(
            {
                "mobile_no": self.phone_number,
                "mobile_no_otp": otp
            }
        ))
        if not resp.ok:
            logger.log("error", "Login failed.")
        return resp

    def save_session(self) -> bool:
        logger.log("info", "Saving current session...")
        with open(self.session_pickle_filename, 'wb') as session_pickle:
            pickle.dump(self.session, session_pickle)
        return True

    def load_session(self) -> Session:
        logger.log("info", "Loading previous session...")
        with open(self.session_pickle_filename, 'rb') as session_pickle:
            return pickle.load(session_pickle)

    def check_if_delivery_slot_available(self, addr_id: str) -> (bool, Response):
        logger.log("info", "Checking delivery slot for addr_id: {}".format(addr_id))
        payload = 'addr_id=' + addr_id
        separate_headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Sec-Fetch-Dest': 'empty',
            'X-CSRFToken': self.session.cookies.get('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': self.BASE_URL,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/80.0.3987.163 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        resp = self.session.post(self.BASE_URL + self.AVAILABILITY_ENDPOINT, data=payload, headers=self.headers)
        if not resp:
            logger.log("error", "Could not check for delivery slot.")
            return False, resp
        data = resp.json()
        if data['status'] == "failure":
            logger.log("info", "No delivery slot is found.")
            return False, resp
        else:
            logger.log("info", "Delivery slot is found.")
            return True, resp

    def visit_cart_page_and_get_address_id(self) -> str:
        logger.log("info", "Visiting cart page...")
        resp = self.session.get(self.BASE_URL + self.CART_ENDPOINT, headers=self.headers)
        addr_id = self._find_address_id(resp.text)
        logger.log("info", "Address Id found")
        return addr_id

    @staticmethod
    def _find_address_id(html: str) -> str:
        return html.split("'addr_id'")[1][:30].split()[1]
