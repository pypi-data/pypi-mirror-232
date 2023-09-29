from time import time
from random import randint
from .creator import color
from .message import message
from .getServer import server
from .requestMaker import make
from .encrypt import encryption
from .socketHandler import handShake

class shad:
    def __init__(self,auth: str):
        self.auth = auth
        self.enc = encryption(auth)
        maker = make(auth,self.enc,server)
        self.sendReq = maker.req
        self.upload = maker.upload

    def getMyGifSet(self):
        return self.sendReq(
            "getMyGifSet",{}
        )
    
    def sendMessage(self,chat_id: str,text: str = None,message_id: str = None,other_data: dict = None):
        data_sendMessage = {
            "is_mute": False,
            "object_guid":chat_id,
            "rnd":str(randint(100000,999999999)),
            "text":text,
            "reply_to_message_id":message_id
        }
        if other_data:
            data_sendMessage.update(other_data)
        return self.sendReq(
            "sendMessage",data_sendMessage)
    
    def forwardMessages(self,from_chat_id: str,to_chat_id: str,message_ids: list):
        return self.sendReq(
            "forwardMessages",{
                "from_object_guid": from_chat_id,
				"message_ids": message_ids,
				"rnd": str(randint(100000,999999999)),
				"to_object_guid": to_chat_id
            })
    
    def setPinMessage(self,chat_id: str,message_id: str):
        return self.sendReq(
            "setPinMessage",{
                "action":"Pin",
			 	"message_id": message_id,
			 	"object_guid": chat_id
            })
    
    def unPinMessage(self,chat_id: str,message_id: str):
        return self.sendReq(
            "setPinMessage",{
                "action":"Unpin",
			 	"message_id": message_id,
			 	"object_guid": chat_id
            })
    
    def editMessage(self,chat_id: str,message_id: str,text: str):
        return self.sendReq(
            "editMessage",{
                "message_id":message_id,
				"object_guid":chat_id,
				"text":text
            })
    
    def deleteMessages(self,chat_id: str,message_ids: list):
        return self.sendReq(
            "deleteMessages",{
                "object_guid":chat_id,
				"message_ids":message_ids,
				"type":"Global"
            })
    
    def deleteUserChat(self,user_guid: str,last_message_id: str):
        return self.sendReq(
            "deleteUserChat",{
                "last_deleted_message_id":last_message_id,
		        "user_guid":user_guid
            })
    
    def deleteChatHistory(self,chat_id: str,last_message_id: str):
        return self.sendReq(
            "deleteChatHistory",{
                "last_message_id": last_message_id,
				"object_guid": chat_id
            })
    
    def blockUser(self,user_guid: str):
        return self.sendReq(
            "setBlockUser",{
                "action": "Block",
				"user_guid": user_guid
            })
    
    def unblockUser(self,user_guid: str):
        return self.sendReq(
            "setBlockUser",{
                "action": "Unblock",
				"user_guid": user_guid
            })
    
    def searchGlobalObjects(self,text: str):
        return self.sendReq(
            "searchGlobalObjects",{
                "search_text":text
            })
    
    def searchMessagesChat(self,text: str):
        return self.sendReq(
            "searchChatMessages",{
                "search_text":text
            })
    
    def getContacts(self,user_guid: str):
        return self.sendReq(
            "getContacts",{
                "start_id":user_guid
            })
    
    def getChats(self,start_id: str = None):
        return self.sendReq(
            "getChats",{
                "start_id":start_id
            })
    
    def getChatsUpdate(self):
        return self.sendReq(
            "getChatsUpdates",{
                "state":round(time()) - 200
            })
    
    def getMessagesInfo(self,chat_id: str,message_ids: list):
        return self.sendReq(
            "getMessagesByID",{
                "object_guid": chat_id,
				"message_ids": message_ids
            })
    
    def getMessagesInterval(self,chat_id: str,middle_message_id: str):
        return self.sendReq(
            "getMessagesInterval",{
                "object_guid":chat_id,
                "middle_message_id":middle_message_id
            })
    
    def getInfoByUsername(self,username: str):
        return self.sendReq(
            "getObjectByUsername",{
                "username":username.split("@")[-1] if "@" in username else username
            })
    
    def seenChats(self,seen_list: list):
        # seen_list -> [{chat_id:message_id},{chat_id2:message_id2},...]
        return self.sendReq(
            "seenChats",{
                "seen_list":seen_list
            })
    
    def getGroupInfo(self,chat_id: str,user_id: str):
        return self.sendReq(
            "getGroupInfo",{
                "group_guid": chat_id
            })
    
    def getGroupAllMembers(self,chat_id: str,start_id: str):
        return self.sendReq(
            "getGroupAllMembers",{
                "group_guid": chat_id,
				"start_id": start_id
            })
    
    def banGroupMember(self,chat_id: str,user_id: str):
        return self.sendReq(
            "banGroupMember",{
                "group_guid": chat_id,
				"member_guid": user_id,
				"action":"Set"
            })
    
    def unbanGroupMember(self,chat_id: str,user_id: str):
        return self.sendReq(
            "banGroupMember",{
                "group_guid": chat_id,
				"member_guid": user_id,
				"action":"Unset"
            })
    
    def leaveGroup(self,chat_id: str):
        return self.sendReq(
            "leaveGroup",{
                "group_guid": chat_id,
            })
    
    def addGroupMembers(self,chat_id: str,user_ids: list):
        return self.sendReq(
            "addGroupMembers",{
                "group_guid": chat_id,
				"member_guids": user_ids
            })
    
    def getGroupOnlineCount(self,chat_id: str):
        return self.sendReq(
            "getGroupOnlineCount",{
                "group_guid": chat_id
            })
    
    def getCommonGroups(self,chat_id: str):
        return self.sendReq(
            "getCommonGroups",{
                "group_guid": chat_id
            })
    
    def getGroupAdminMembers(self,chat_id: str):
        return self.sendReq(
            "getGroupAdminMembers",{
                "group_guid": chat_id
            })
    
    def setGroupTimer(self,chat_id: str,time_slow: str):
        return self.sendReq(
            "editGroupInfo",{
                "group_guid": chat_id,
				"slow_mode": time_slow,
				"updated_parameters":["slow_mode"]
            })
    
    def setGroupAdmin(self,chat_id: str,user_id: str):
        return self.sendReq(
            "setGroupAdmin",{
                "group_guid": chat_id,
				"access_list":["SetJoinLink"],
				"action": "SetAdmin",
				"member_guid": user_id
            })
    
    def unsetGroupAdmin(self,chat_id: str,user_id: str):
        return self.sendReq(
            "setGroupAdmin",{
                "group_guid": chat_id,
				"action": "UnsetAdmin",
				"member_guid": user_id
            })
    
    def getChannelInfo(self,chat_id: str,user_ids: list):
        return self.sendReq(
            "getChannelInfo",{
                "channel_guid": chat_id
            })
    
    def getChannelAllMembers(self,channel_guid: str,text: str = None,start_id: str = None):
        return self.sendReq(
            "getChannelAllMembers",{
                "channel_guid":channel_guid,
				"search_text":text,
				"start_id":start_id,
            })
    
    def addChannelMembers(self,chat_id: str,user_ids: list):
        return self.sendReq(
            "getCommonGroups",{
                "channel_guid": chat_id,
				"member_guids": user_ids
            })
    
    def channelPreviewByJoinLink(self,link: str):
        return self.sendReq(
            "channelPreviewByJoinLink",{
                "hash_link": link.split("/")[-1]
            })
    
    def joinChannelByLink(self,link: str):
        return self.sendReq(
            "joinChannelByLink",{
                "hash_link": link.split("/")[-1]
            })
    
    def joinChannelByGuid(self,channel_guid: str):
        return self.sendReq(
            "joinChannelAction",{
                "action": "Join",
				"channel_guid": channel_guid
            })
    
    def leaveChannel(self,channel_guid: str):
        return self.sendReq(
            "joinChannelAction",{
                "action": "Leave",
				"channel_guid": channel_guid
            })
    
    def getLinkFromAppUrl(self,app_url: str):
        return self.sendReq(
            "getLinkFromAppUrl",{
                "app_url":app_url
            })
    
    def sendLocation(self,chat_id: str,location: list,message_id: str):
        return self.sendMessage(
            chat_id,
            message_id=message_id,
            other_data={
                "location":{
                    "latitude": location[0],
                    "longitude": location[1]
            }},
        )
    
    def sendFile(self,chat_id: str,file: str,text: str = None,message_id: str = None,file_name:str = None):
        uploaded_file = self.upload(file,file_name if file_name else None)
        if type(uploaded_file) is dict:
            return uploaded_file
        return self.sendMessage(
            chat_id,
            message_id=message_id,
            text=text,
            other_data={
                "file_inline": {
                    "file_id": uploaded_file[1],
                    "dc_id": uploaded_file[2],
                    "file_name": uploaded_file[3],
                    "size": uploaded_file[4],
                    "mime": uploaded_file[5],
                    "access_hash_rec": uploaded_file[0],
                    "type":"File",
            }},
        )
    
    def sendMusic(self,chat_id: str,file: str,text: str = None,message_id: str = None,file_name:str = None):
        uploaded_file = self.upload(file,file_name if file_name else None)
        if type(uploaded_file) is dict:
            return uploaded_file
        return self.sendMessage(
            chat_id,
            message_id=message_id,
            text=text,
            other_data={
                "file_inline": {
                    "file_id": uploaded_file[1],
                    "dc_id": uploaded_file[2],
                    "file_name": uploaded_file[3],
                    "size": uploaded_file[4],
                    "mime": uploaded_file[5],
                    "access_hash_rec": uploaded_file[0],
                    "time": 2721,
                    "music_performer":"X CODER",
                    "type":"Music",
            }},
        )
    
    def sendVoice(self,chat_id: str,file: str,text: str = None,message_id: str = None,file_name:str = None):
        uploaded_file = self.upload(file,file_name if file_name else None)
        if type(uploaded_file) is dict:
            return uploaded_file
        return self.sendMessage(
            chat_id,
            message_id=message_id,
            text=text,
            other_data={
                "file_inline": {
                    "file_id": uploaded_file[1],
                    "dc_id": uploaded_file[2],
                    "file_name": uploaded_file[3],
                    "size": uploaded_file[4],
                    "mime": uploaded_file[5],
                    "access_hash_rec": uploaded_file[0],
                    "time": 2721,
                    "type":"Voice",
            }},
        )
    
    def sendImage(self,chat_id: str,file: str,text: str = None,message_id: str = None,file_name:str = None):
        uploaded_file = self.upload(file,file_name if file_name else None)
        if type(uploaded_file) is dict:
            return uploaded_file
        return self.sendMessage(
            chat_id,
            message_id=message_id,
            text=text,
            other_data={
                "file_inline": {
                    "file_id": uploaded_file[1],
                    "dc_id": uploaded_file[2],
                    "file_name": uploaded_file[3],
                    "size": uploaded_file[4],
                    "mime": uploaded_file[5],
                    "access_hash_rec": uploaded_file[0],
                    "thumb_inline": "/9j/4AAQSkZJRgABAQAAAQABAAD/4gIoSUNDX1BST0ZJTEUAAQEAAAIYAAAAAAQwAABtbnRyUkdC\nIFhZWiAAAAAAAAAAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAA\nAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlk\nZXNjAAAA8AAAAHRyWFlaAAABZAAAABRnWFlaAAABeAAAABRiWFlaAAABjAAAABRyVFJDAAABoAAA\nAChnVFJDAAABoAAAAChiVFJDAAABoAAAACh3dHB0AAAByAAAABRjcHJ0AAAB3AAAADxtbHVjAAAA\nAAAAAAEAAAAMZW5VUwAAAFgAAAAcAHMAUgBHAEIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFhZWiAA\nAAAAAABvogAAOPUAAAOQWFlaIAAAAAAAAGKZAAC3hQAAGNpYWVogAAAAAAAAJKAAAA+EAAC2z3Bh\ncmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABYWVogAAAAAAAA9tYAAQAAAADT\nLW1sdWMAAAAAAAAAAQAAAAxlblVTAAAAIAAAABwARwBvAG8AZwBsAGUAIABJAG4AYwAuACAAMgAw\nADEANv/bAEMADgoLDQsJDg0MDRAPDhEWJBcWFBQWLCAhGiQ0Ljc2My4yMjpBU0Y6PU4+MjJIYklO\nVlhdXl04RWZtZVpsU1tdWf/bAEMBDxAQFhMWKhcXKlk7MjtZWVlZWVlZWVlZWVlZWVlZWVlZWVlZ\nWVlZWVlZWVlZWVlZWVlZWVlZWVlZWVlZWVlZWf/AABEIAEgAWgMBIgACEQEDEQH/xAAaAAEAAwEB\nAQAAAAAAAAAAAAAAAwQFAgYH/8QANxAAAQMCAgYGBwkAAAAAAAAAAQACAwQRBSESEzFBUWEUIiMy\nUnEGM2KxwdLwFXKBg5GTodHh/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAH/xAAUEQEAAAAAAAAAAAAA\nAAAAAAAA/9oADAMBAAIRAxEAPwD50iIqgiIgIiICIiAiIgIiICIiDuMMLu0c5reLW3PvCnDKIm3S\nKgfkD51VUkL42v7VmnGdoBsfwPFBqNwTpOGy1mH1TarUZyw6BbIxvitvHkshaTW1eD1ENfRTF0RP\nZTtGTvZcNx4tP8jNajaGgx94rYJYqDR61ZCTkwb3s5HhuJQZmFYNLiMM9S+VlNRU7byVEgOiDuaA\nMyeQ+IvBLBQMNm1ssvNlP/bgtHEK2XGJYcMwqB0dDB6qIG1+L3n4nZdZVU2CE6mBwlLe9MNjj7PL\nntPLYgjlbAPUySv+/GG+5xUSIgIiICIiAiKSIMLrykhg222nkEGz6PSmCGpkrC37KI0ZWPF9Y62Q\naPFvuNixpjG6Z5ha5kRPVa43IHmrDnT4lPFDEyzWjRjib3WD6zJWhHW0uEno0UcdVp5VMhHeHhby\nQSa1kno6YcK7J7etWsveR7fEDvaM8t1/18+tOrp3YfNFW0MrjA46UUg2tPA81UqHxzEysa2N577B\nk2/FvAcvoBXREQEREBERB03RB6wJHI2XelBf1cn7g+VRIgutr9TTPhpohFrO+/Su4jhfgqSIgt0l\nc+mZJE5olgkHWiccjzHAqNz4HbIXt8pP8UCIO3mM9xrh5uv8AuERAREQEREBERAREQEREBERAREQ\nf//Z\n",
                    "width": 251,
                    "height": 201,
                    "type":"Image",
            }},
        )
    
    def sendVideo(self,chat_id: str,file: str,text: str = None,message_id: str = None,file_name:str = None):
        uploaded_file = self.upload(file,file_name if file_name else None)
        if type(uploaded_file) is dict:
            return uploaded_file
        return self.sendMessage(
            chat_id,
            message_id=message_id,
            text=text,
            other_data={
                "file_inline": {
                    "file_id": uploaded_file[1],
                    "dc_id": uploaded_file[2],
                    "file_name": uploaded_file[3],
                    "size": uploaded_file[4],
                    "mime": uploaded_file[5],
                    "access_hash_rec": uploaded_file[0],
                    "thumb_inline": "/9j/4AAQSkZJRgABAQAAAQABAAD/4gIoSUNDX1BST0ZJTEUAAQEAAAIYAAAAAAQwAABtbnRyUkdC\nIFhZWiAAAAAAAAAAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAA\nAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlk\nZXNjAAAA8AAAAHRyWFlaAAABZAAAABRnWFlaAAABeAAAABRiWFlaAAABjAAAABRyVFJDAAABoAAA\nAChnVFJDAAABoAAAAChiVFJDAAABoAAAACh3dHB0AAAByAAAABRjcHJ0AAAB3AAAADxtbHVjAAAA\nAAAAAAEAAAAMZW5VUwAAAFgAAAAcAHMAUgBHAEIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFhZWiAA\nAAAAAABvogAAOPUAAAOQWFlaIAAAAAAAAGKZAAC3hQAAGNpYWVogAAAAAAAAJKAAAA+EAAC2z3Bh\ncmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABYWVogAAAAAAAA9tYAAQAAAADT\nLW1sdWMAAAAAAAAAAQAAAAxlblVTAAAAIAAAABwARwBvAG8AZwBsAGUAIABJAG4AYwAuACAAMgAw\nADEANv/bAEMADgoLDQsJDg0MDRAPDhEWJBcWFBQWLCAhGiQ0Ljc2My4yMjpBU0Y6PU4+MjJIYklO\nVlhdXl04RWZtZVpsU1tdWf/bAEMBDxAQFhMWKhcXKlk7MjtZWVlZWVlZWVlZWVlZWVlZWVlZWVlZ\nWVlZWVlZWVlZWVlZWVlZWVlZWVlZWVlZWVlZWf/AABEIAEgAWgMBIgACEQEDEQH/xAAaAAEAAwEB\nAQAAAAAAAAAAAAAAAwQFAgYH/8QANxAAAQMCAgYGBwkAAAAAAAAAAQACAwQRBSESEzFBUWEUIiMy\nUnEGM2KxwdLwFXKBg5GTodHh/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAH/xAAUEQEAAAAAAAAAAAAA\nAAAAAAAA/9oADAMBAAIRAxEAPwD50iIqgiIgIiICIiAiIgIiICIiDuMMLu0c5reLW3PvCnDKIm3S\nKgfkD51VUkL42v7VmnGdoBsfwPFBqNwTpOGy1mH1TarUZyw6BbIxvitvHkshaTW1eD1ENfRTF0RP\nZTtGTvZcNx4tP8jNajaGgx94rYJYqDR61ZCTkwb3s5HhuJQZmFYNLiMM9S+VlNRU7byVEgOiDuaA\nMyeQ+IvBLBQMNm1ssvNlP/bgtHEK2XGJYcMwqB0dDB6qIG1+L3n4nZdZVU2CE6mBwlLe9MNjj7PL\nntPLYgjlbAPUySv+/GG+5xUSIgIiICIiAiKSIMLrykhg222nkEGz6PSmCGpkrC37KI0ZWPF9Y62Q\naPFvuNixpjG6Z5ha5kRPVa43IHmrDnT4lPFDEyzWjRjib3WD6zJWhHW0uEno0UcdVp5VMhHeHhby\nQSa1kno6YcK7J7etWsveR7fEDvaM8t1/18+tOrp3YfNFW0MrjA46UUg2tPA81UqHxzEysa2N577B\nk2/FvAcvoBXREQEREBERB03RB6wJHI2XelBf1cn7g+VRIgutr9TTPhpohFrO+/Su4jhfgqSIgt0l\nc+mZJE5olgkHWiccjzHAqNz4HbIXt8pP8UCIO3mM9xrh5uv8AuERAREQEREBERAREQEREBERAREQ\nf//Z\n",
                    "width": 251,
                    "height": 201,
                    "time": 2721,
                    "type":"Video",
            }},
        )
    
    def onMessage(self,type_update: str,filter_type: list = None,filter_chat_id: list = None):
        if type_update == "getChatsUpdate":
            message_id_geted = []
            while True:
                try:
                    for chat in self.getChatsUpdate()["chats"]:
                        msg = message(chat)
                        if msg.message_id not in message_id_geted:
                            message_id_geted.append(msg.message_id)
                            yield msg
                except:continue
        elif type_update == "socket":
            for getSc in handShake(self.auth,self.server_shad.socket,self.enc.decrypt):
                if "chat_updates" in getSc and "message_updates" in getSc:
                    yield message(getSc)
        else:
            raise('update type not defind')
    
    def updateProfile(self,first_name=None,last_name=None,bio=None,username=None):
        updated_data , res = {} , {}
        if first_name:updated_data.update({"first_name":first_name})
        if last_name:updated_data.update({"last_name":last_name})
        if bio:updated_data.update({"bio":bio})
        if updated_data:
            res.update({"updateProfile":self.sendReq("updateProfile",updated_data)})
        if username:
            res.update({"username":self.sendReq(
                "updateUsername",{
                    "username":username
                })})
        return res