from websocket import create_connection as cn
from .clientData import client_android
from .getServer import server
from json import dumps,loads

    
def handShake(auth,server,dec):
    print("connect to the socket...")
    while True:
        soc = cn(server)
        soc.send(dumps({
            "api_version": "4",
            "auth": auth,
            "client": client_android,
            "data_enc": "/G/6BO6surMG/WXecko9DA\u003d\u003d\n",
            "method": "handShake"
        }))
        if loads(soc.recv()) == {"status":"OK", "status_det":"OK"}:
            print("connected !")
            while True:
                try:
                    recv = loads(soc.recv())
                    if recv["type"] == "messenger":
                        yield loads(dec(recv["data_enc"]))
                except:break