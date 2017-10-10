# -*- coding: utf-8 -*-
'''
Created on 2017. 10. 10.
@author: HyechurnJang
'''

import re
import json
import jzlib
import pygics
import requests

'''
Message Type
# 1 on 1
{
  "roomType": "direct",
  "created": "2017-10-10T12:42:21.454Z",
  "personId": "",
  "personEmail": "hyjang@cisco.com",
  "roomId": "",
  "id": ""
}
# @BOT at Space
{
  "roomType": "group",
  "created": "2017-10-10T12:43:42.021Z",
  "personId": "",
  "personEmail": "hyjang@cisco.com",
  "mentionedPeople": [
    "{metioned people ID}", ...
  ],
  "roomId": "",
  "id": ""
}
'''

SPARK_WEBHOOK_URL = 'https://api.ciscospark.com/v1/webhooks/'
SPARK_MESSAGE_URL = 'https://api.ciscospark.com/v1/messages/'
SPARK_PERSON_URL = 'https://api.ciscospark.com/v1/people/'

class Bot(jzlib.Inventory):
    
    def __init__(self, bot_key, bot_id, bot_name, bot_server):
        jzlib.Inventory.__init__(self)
        
        # Set Bot Descriptions
        self.id = bot_id
        self.key = bot_key
        self.name = bot_name
        self.email = bot_id + '@sparkbot.io'
        self.server = 'http://%s/%s' % (bot_server, bot_id)
        self.hook = bot_id + 'hook'
        self.headers = {'Content-type' : 'application/json; charset=utf-8', 'Authorization' : 'Bearer %s' % bot_key}
        
        # Register Webhook
        try:
            resp = requests.get(SPARK_WEBHOOK_URL, headers=self.headers)
            webhooks = resp.json()['items']
            isHook = False
            for webhook in webhooks:
                if webhook['name'] == self.hook and webhook['targetUrl'] == self.server: isHook = True
                else:
                    try: requests.delete(SPARK_WEBHOOK_URL + webhook['id'], headers=self.headers)
                    except: pass
            if not isHook:
                resp = requests.post(SPARK_WEBHOOK_URL, headers=self.headers, json={'name' : self.hook, 'targetUrl' : self.server,'resource' : 'messages', 'event' : 'created'})
                if resp.status_code != 200: raise Exception('webhook failed')
        except: raise Exception('webhook failed')
        
    class Message(jzlib.Inventory):
        
        def create(self, room_id=None, person_id=None, person_email=None, text=None, markdown=None, file=None):
            data = {}
            if room_id: data['roomId'] = room_id
            elif person_id: data['toPersonId'] = person_id
            elif person_email: data['toPersonEmail'] = person_email
            else: raise Exception('incorrect target to send')
            if text: data['text'] = text
            elif markdown: data['markdown'] = markdown
            elif file: data['file'] = [file]
            else: raise Exception('incorrect data to send')
            resp = requests.post(SPARK_MESSAGE_URL, headers=(~self).headers, json=data)
            if resp.status_code != 200: raise Exception('sending message failed')

class Message:
    
    class MarkDown:
        def __init__(self, content): self.content = content
    
    class File:
        def __init__(self, content): self.content = content
        
    class Bypass(Exception): pass
    
    @classmethod
    def encoding(cls, text):
        if isinstance(text, str) or isinstance(text, unicode): return text
        else:
            try: return text.decode('utf-8')
            except:
                try: return text.decode('utf-16')
                except: return Message.getErrorMessage('encoding failed')
    
    @classmethod
    def getErrorMessage(cls, error):
        return 'Ouch! I have error~~ d[X_X]b\nReason : %s' % error
    
    def __init__(self, bot, req):
        self.bot = bot
        try:
            raw_data = req.data['data']
            self.msg_id = raw_data['id']
            self.room_id = raw_data['roomId']
            self.person_id = raw_data['personId']
            self.person_email = raw_data['personEmail']
        except: raise Exception('parse request failed')
        if self.person_email == bot.email: raise Message.Bypass()
        try:
            msg_resp, psn_resp = pygics.Burst(
            )(requests.get, SPARK_MESSAGE_URL + self.msg_id, headers=bot.headers
            )(requests.get, SPARK_PERSON_URL + self.person_id, headers=bot.headers
            ).do()
            msg_data = msg_resp.json()
            psn_data = psn_resp.json()
            self.who = psn_data['displayName']
            self.text = msg_data['text']
        except Exception as e: raise Exception('retriving details failed')
        if msg_resp.status_code != 200 or psn_resp.status_code != 200: raise Exception('retriving details failed')
        kv = re.match('^%s\s*(?P<text>.*)' % bot.name, self.text)
        if kv:
            self.text = kv.group('text')
            self.space = True
        else: self.space = False
        self.raw_request = raw_data
        self.raw_message = msg_data
        self.raw_person = psn_data
        
        print json.dumps(raw_data, indent=2)
        print json.dumps(psn_data, indent=2)
        print json.dumps(msg_data, indent=2)
    
    def reply(self, content):
        if isinstance(content, str) or isinstance(content, unicode):
            if self.space: content = u'To : %s\n%s' % (self.who, Message.encoding(content))
            else: content = Message.encoding(content)
            self.bot.Message.create(room_id=self.room_id, text=content)
        elif isinstance(content, Message.MarkDown): self.bot.Message.create(room_id=self.room_id, markdown=Message.encoding(content.content))
        elif isinstance(content, Message.File): self.bot.Message.create(room_id=self.room_id, file=Message.encoding(content.content))
        else: self.bot.Message.create(room_id=self.room_id, text=Message.getErrorMessage('unsupport content type'))

    def replyError(self, error):
        self.bot.Message.create(room_id=self.room_id, text=Message.getErrorMessage(str(error)))
