from requests.sessions import Session
from .clientData import client_android
from json import dumps

class server:
    try:
        url = "https://shgetdcmess.iranlms.ir/"
        session = Session()
        data = session.get(url).json()["data"]
        API = data["API"][data["default_api"]]
        socket = data["socket"][data["default_socket"]]
    except:
        raise KeyError("EROOR get server") 