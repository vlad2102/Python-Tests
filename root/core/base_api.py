import requests


class BaseAPI:
    def __init__(self):
        self.session = requests.Session()

    def get_cookie(self, name: str) -> str:
        return self.session.cookies.get_dict()[name]
