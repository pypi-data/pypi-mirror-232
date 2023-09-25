import base64
import os
import pyotp
import requests
import pathlib

from datetime import datetime
from urllib.parse import parse_qs, urlparse

from fyers_apiv3 import fyersModel

from fyers_apiv3.FyersWebsocket import data_ws


class FyersTokenManager:
    def __init__(self, config):
        self.username = config["username"]
        self.totp_key = config["totp_key"]
        self.pin = config["pin"]
        self.client_id = config["client_id"]
        self.secret_key = config["secret_key"]
        self.redirect_uri = config["redirect_uri"]

        self.__data_path = None
        self.__logs_path = None
        self.__file_name = None

        self.http_access_token = None
        self.ws_access_token = None

        self.__set_access_token_file_name()
        self.__initialize()

    def get_http_client(self):
        return fyersModel.FyersModel(
            client_id=self.client_id,
            token=self.http_access_token,
            log_path=str(self.__logs_path),
        )

    def get_ws_client(self, symbols, on_message):
        def on_connect(fyers, symbols):
            fyers.subscribe(symbols=symbols, data_type="SymbolUpdate")
            fyers.keep_running()

        fyers = data_ws.FyersDataSocket(
            access_token=self.ws_access_token,
            log_path=str(self.__logs_path),
            litemode=False,
            write_to_file=False,
            reconnect=True,
            on_connect=lambda: on_connect(fyers, symbols),
            on_error=lambda error: print(error),
            on_message=on_message,
        )

        return fyers

    def __set_access_token_file_name(self):
        home_directory = os.path.expanduser("~")

        self.__data_path = pathlib.Path(
            f"{home_directory}/fyers_token_manager/data/{self.username}"
        )

        self.__logs_path = pathlib.Path(f"{home_directory}/fyers_token_manager/logs")

        if not self.__data_path.exists():
            self.__data_path.mkdir(parents=True, exist_ok=True)

        if not self.__logs_path.exists():
            self.__logs_path.mkdir()

        self.__file_name = os.path.join(
            self.__data_path, datetime.now().strftime("%Y-%m-%d")
        )

    def __set_initial_values(self, token):
        self.http_access_token = token
        self.ws_access_token = f"{self.client_id}:{self.http_access_token}"

    def __initialize(self):
        try:
            token = self.__read_file()
            self.__set_initial_values(token)
        except FileNotFoundError:
            token = self.__setup()
            self.__set_initial_values(token)

    def __read_file(self):
        with open(f"{self.__file_name}", "r") as f:
            token = f.read()

        return token

    def __write_file(self, token):
        with open(f"{self.__file_name}", "w") as f:
            f.write(token)

    def __get_token(self):
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        }

        s = requests.Session()
        s.headers.update(headers)

        data1 = f'{{"fy_id":"{base64.b64encode(f"{self.username}".encode()).decode()}","app_id":"2"}}'
        r1 = s.post("https://api-t2.fyers.in/vagator/v2/send_login_otp_v2", data=data1)
        assert r1.status_code == 200, f"Error in r1:\n {r1.json()}"

        request_key = r1.json()["request_key"]
        data2 = (
            f'{{"request_key":"{request_key}","otp":{pyotp.TOTP(self.totp_key).now()}}}'
        )
        r2 = s.post("https://api-t2.fyers.in/vagator/v2/verify_otp", data=data2)
        assert r2.status_code == 200, f"Error in r2:\n {r2.text}"

        request_key = r2.json()["request_key"]
        data3 = f'{{"request_key":"{request_key}","identity_type":"pin","identifier":"{base64.b64encode(f"{self.pin}".encode()).decode()}"}}'
        r3 = s.post("https://api-t2.fyers.in/vagator/v2/verify_pin_v2", data=data3)
        assert r3.status_code == 200, f"Error in r3:\n {r3.json()}"

        headers = {
            "authorization": f"Bearer {r3.json()['data']['access_token']}",
            "content-type": "application/json; charset=UTF-8",
        }
        data4 = f'{{"fyers_id":"{self.username}","app_id":"{self.client_id[:-4]}","redirect_uri":"{self.redirect_uri}","appType":"100","code_challenge":"","state":"abcdefg","scope":"","nonce":"","response_type":"code","create_cookie":true}}'
        r4 = s.post("https://api.fyers.in/api/v2/token", headers=headers, data=data4)
        assert r4.status_code == 308, f"Error in r4:\n {r4.json()}"

        parsed = urlparse(r4.json()["Url"])
        auth_code = parse_qs(parsed.query)["auth_code"][0]

        session = fyersModel.SessionModel(
            client_id=self.client_id,
            secret_key=self.secret_key,
            redirect_uri=self.redirect_uri,
            response_type="code",
            grant_type="authorization_code",
        )

        session.set_token(auth_code)
        response = session.generate_token()

        return response["access_token"]

    def __setup(self):
        token = self.__get_token()
        self.__write_file(token)

        return token
