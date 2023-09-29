from json import dumps,loads
from .getServer import server
from .encrypt import encryption
from .clientData import client_android

class make:
    def __init__(self,auth: str, encrypt, server):
        self.auth = auth
        self.server = server
        self.enc = encrypt
    
    def req(self,method: str,data: dict):
        try:
            data = self.server.session.post(
                self.server.API,
                data=dumps({
                    "api_version" : "4",
                    "auth" : self.auth,
                    "client" : client_android,
                    "data_enc" : self.enc.encrypt(dumps(data)),
                    "method" : method
                })
            ).json()
            if "data_enc" in data:
                return loads(self.enc.decrypt(data["data_enc"]))
            else:
                return data
        except:pass

    def upload(self,file: str,fileName: str = None):
        try:
            if type(file) is bytes:
                bytef = file
                file_name = fileName if fileName else f"ShadiX.txt"
            elif "http" in file or "https" in file:
                try:
                    bytef = self.server.session.get(file).content
                    mime = file.split(".")[-1] if "." in file else "txt"
                    file_name = fileName if fileName else f"ShadiX.{mime}"
                except:
                    return {"status":"EOOR","message":"EROOR request get file by link"}
            else:
                bytef = open(file,"rb").read()
                file_name = fileName if fileName else file
            size = len(bytef)
            try:
                data = self.req(
                    "requestSendFile",{
                        "file_name": file_name,
                        "mime": file_name.split(".")[-1],
                        "size": size
                })
            except:
                return {"status":"EOOR","message":"EROOR request send file"}
            
            url = data["upload_url"]

            header = {
                "auth":self.auth,
                "Host":url.replace("https://","").replace("/UploadFile.ashx",""),
                "chunk-size": str(size),
                "file-id": str(data["id"]),
                "access-hash-send": data["access_hash_send"],
                "content-type": "application/octet-stream",
                "content-length": str(size),
                "accept-encoding": "gzip",
                "user-agent": "okhttp/3.12.1"
            }

            if len(bytef) <= 131072:
                header["part-number"], header["total-part"] = "1","1"
                send_data = self.server.session.post(url,headers=header,data=bytef)
            else:
                t = len(bytef) // 131072 + 1
                for i in range(1, t+1):
                    k = (i - 1) * 131072
                    if i != t:
                        header["chunk-size"], header["part-number"], header["total-part"] = "131072", str(i),str(t)
                        send_data = self.server.session.post(url,headers=header,data=bytef[k:k + 131072])
                        print("\r" + f"{round(k / 1024) / 1000} MB |", end=f" {round(len(bytef) / 1024) / 1000} MB ")
                    else:
                        header["chunk-size"], header["part-number"], header["total-part"] = str(len(bytef[k:])), str(i),str(t)
                        send_data = self.server.session.post(url,headers=header,data=bytef[k:])
                        print("\r" + f"{round(len(bytef) / 1024) / 1000} MB |", end=f" {round(len(bytef) / 1024) / 1000} MB ")
                print()
            del bytef
            return send_data.json()["data"]["access_hash_rec"],data["id"],data["dc_id"],file_name,size,file_name.split(".")[-1]
        except:
            return data