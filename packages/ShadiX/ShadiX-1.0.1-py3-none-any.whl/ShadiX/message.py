class message:
    def __init__(self,data):
        self.data = data
    
    @property
    def chat_id(self):
        try:
            return self.data["message_updates"][0]["object_guid"] if 'message_updates' in self.data else self.data['object_guid']
        except:pass

    @property
    def author_id(self):
        try:
            return self.data["message_updates"][0]["message"]["author_object_guid"] if 'message_updates' in self.data else self.data['last_message']['author_object_guid']
        except:pass

    @property
    def message_id(self):
        try:
            return self.data["message_updates"][0]["message_id"] if 'message_updates' in self.data else self.data['last_message_id']
        except:pass

    @property
    def reply_to_message_id(self):
        try:
            return self.data["message_updates"][0]["message"]["reply_to_message_id"]
        except:pass

    @property
    def text(self):
        try:
            return self.data["message_updates"][0]["message"]["text"] if 'message_updates' in self.data else self.data['last_message']['text']
        except:pass

    @property
    def chat_type(self):
        try:
            return self.data["message_updates"][0]["type"] if 'message_updates' in self.data else self.data['abs_object']['type']
        except:pass

    @property
    def author_type(self):
        try:
            return self.data["message_updates"][0]["message"]["author_type"] if 'message_updates' in self.data else self.data['last_message']['author_type']
        except:pass

    @property
    def message_type(self):
        try:
            return self.data["message_updates"][0]["message"]["type"] if 'message_updates' in self.data else self.data['last_message']['type']
        except:pass

    @property
    def is_forward(self):
        try:
            return "forwarded_from" in self.data["message_updates"][0]["message"]
        except:pass
        
    @property
    def forward_type(self):
        if self.is_forward():
            try:
                return self.data["message_updates"][0]["message"]["forwarded_from"]["type_from"]
            except:pass
        
    @property
    def forward_id(self):
        if self.is_forward():
            try:
                return self.data["message_updates"][0]["message"]["forwarded_from"]["object_guid"]
            except:pass
        
    @property
    def forward_message_id(self):
        if self.is_forward():
            try:
                return self.data["message_updates"][0]["message"]["forwarded_from"]["message_id"]
            except:pass

    @property
    def chat_title(self):
        try:
            title = self.data["show_notifications"][0]
            return title.get("author_title",title["title"]) if 'show_notifications' in self.data else self.data['abs_object'].get('title', f"{self.data['abs_object']['first_name']} {self.data['abs_object']['last_name']}") if "abs_object" in self.data else None
        except:pass

    @property
    def is_event(self):
        try:
            return "event_data" in self.data["message_updates"][0]["message"] if 'message_updates' in self.data else self.message_type() == 'Other'
        except:pass

    @property
    def event_type(self):
        if self.is_event():
            try:
                return self.data["message_updates"][0]["message"]["event_data"]
            except:pass

    @property
    def event_id(self):
        if self.is_event():
            try:
                return self.data["message_updates"][0]["message"]["event_data"]["performer_object"]
            except:pass

    @property 
    def count_unseen(self):
        try:
            return self.data["chat_updates"][0]["chat"]["count_unseen"]
        except:pass