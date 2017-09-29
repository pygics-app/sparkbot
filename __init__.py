# -*- coding: utf-8 -*-
'''
Created on 2017. 4. 12.
@author: HyechurnJang
'''

import re
import types
import pygics
import requests

SPARK_WEBHOOK_URL = 'https://api.ciscospark.com/v1/webhooks/'
SPARK_MESSAGE_URL = 'https://api.ciscospark.com/v1/messages/'
SPARK_PERSON_URL = 'https://api.ciscospark.com/v1/people/'

def __registerHook__(key, name, url):
    headers = {'Content-type' : 'application/json; charset=utf-8', 'Authorization' : 'Bearer %s' % key}
    try:
        resp = requests.get(SPARK_WEBHOOK_URL, headers=headers)
        whs = resp.json()['items']
        isHook = False
        for wh in whs:
            if wh['name'] == name and wh['targetUrl'] == url: isHook = True
            else:
                try: requests.delete(SPARK_WEBHOOK_URL + wh['id'], headers=headers)
                except: pass
        if not isHook:
            resp = requests.post(SPARK_WEBHOOK_URL, headers=headers,
                                 json={'name' : name,
                                       'targetUrl' : url,
                                       'resource' : 'messages',
                                       'event' : 'created'})
            if resp.status_code == 200: return True
    except: return False
    return False

def __replyError__(key, room_id, err_msg='unknown error'):
    headers = {'Content-type' : 'application/json; charset=utf-8', 'Authorization' : 'Bearer %s' % key}
    try:
        requests.post(SPARK_MESSAGE_URL, headers=headers,
                      json={'roomId':room_id,
                            'text':'Ouch! I have error~~ d[X_X]b\n%s' % err_msg})
    except: return 'failed'
    return 'failed'

def __encoding_str__(text):
    if isinstance(text, str) or isinstance(text, unicode):
        return text
    else:
        try:
            return text.decode('utf-8')
        except:
            return text.decode('utf-16')

class MarkDown:
    def __init__(self, text): self.text = text
    
class Key:
    
    class Pattern:
    
        def __init__(self, pattern):
            self.original = pattern
            self.keys = []
            ref = pattern
            while True:
                kv = re.search('{{(?P<key>\w+):.*}}', ref)
                if kv:
                    key = kv.group(1)
                    self.keys.append(kv.group(1))
                    ref = ref.replace('{{%s:' % key, '')
                else: break
            
            if self.keys:
                ref = pattern
                for key in self.keys: ref = ref.replace('{{%s:' % key, '(?P<%s>' % key)
                self.pattern = re.compile(ref.replace('}}', ')'), re.UNICODE)
                self.mtype = True
            else:
                self.pattern = re.compile(pattern, re.UNICODE)
                self.mtype = False
        
        def match(self, text):
            if self.mtype:
                result = {}
                kv = self.pattern.match(text)
                if kv:
                    for key in self.keys: result[key] = unicode(kv.group(key))
                return result
            else:
                return True if self.pattern.search(text) else False
    
    def __init__(self, patterns, reply, next=None):
        if not isinstance(patterns, list): patterns = [patterns]
        self.patterns = []
        for pattern in patterns: self.patterns.append(Key.Pattern(pattern))
        self.reply = reply
        self.next = next
    
    def match(self, text):
        for pattern in self.patterns:
            result = pattern.match(text)
            if result: return pattern.original, result
        return None, None

class Talk:
    
    def __init__(self, _id, init, dismatch, rewind=True):
        self._id = _id
        self.init = init
        self.dismatch = dismatch
        self.rewind = rewind
        self.keys = []
    
    def add(self, *keys):
        for key in keys: self.keys.append(key)
        return self
        
    def do(self, user, history, text):
        for key in self.keys:
            k, result = key.match(text)
            if result:
                if isinstance(key.reply, types.FunctionType): reply = key.reply(user, history, result)
                else: reply = key.reply
                history.append({'_id' : self._id, 'text' : text, 'key' : k, 'result' : result, 'reply' : reply})
                return reply, key.next
        if self.rewind: return self.dismatch, self._id
        else: return self.dismatch, None

class TalkBox:
    
    def __init__(self, locking, error='Critical Error'):
        self.locking = locking
        self.error = error
        self.talk = {}
        self.context = {}
        self.init = None
    
    def add(self, *talks):
        for talk in talks:
            if not self.init: self.init = talk
            self.talk[talk._id] = talk
        return self
    
    def do(self, data, user, text):
        if user not in self.context:
            self.context[user] = {'curr' : self.init, 'hist' : [], 'lock' : pygics.Lock()}
        uref = self.context[user]
        curr = uref['curr']
        hist = uref['hist']
        lock = uref['lock']
        if lock.acquire(False):
            try:
                reply, next = curr.do(user, hist, text)
                if next != None and next != self.init._id:
                    next = self.talk[next]
                else:
                    next = self.init
                    uref['hist'] = []
                uref['curr'] = next
                next_reply = next.init
            except Exception as e:
                reply = self.error
                next_reply = str(e)
            lock.release()
            if isinstance(reply, types.FunctionType): reply = reply(data, user, text)
            if isinstance(next_reply, types.FunctionType): next_reply = reply(data, user, text)
            return '%s\n%s' % (reply, next_reply)
        else: return self.locking

def msg(key, room_id, text):
    resp = requests.post(SPARK_MESSAGE_URL,
                         headers={'Content-type' : 'application/json; charset=utf-8', 'Authorization' : 'Bearer %s' % key},
                         json={'roomId' : room_id, 'text' : text})
    if resp.status_code == 200: return True
    return False

def message(key, bot_name, bot_id, bot_server):
    
    __registerHook__(key, bot_id + 'Hook', 'http://%s/sparkbot/%s' % (bot_server, bot_id))
    bot_email = bot_id + '@sparkbot.io'
    
    def botfunc(func):
        def decofunc(req):
            try:
                req_data = req.data['data']
                msg_id = req_data['id']
                room_id = req_data['roomId']
                person_id = req_data['personId']
                person_email = req_data['personEmail']
            except: return 'failed'
            if person_email == bot_email: return 'bypass'
            
            headers = {'Content-type' : 'application/json; charset=utf-8', 'Authorization' : 'Bearer %s' % key}
            
            try:
                msg_resp, psn_resp = pygics.Burst(
                )(requests.get, SPARK_MESSAGE_URL + msg_id, headers=headers
                )(requests.get, SPARK_PERSON_URL + person_id, headers=headers
                ).do()
            except Exception as e: return __replyError__(key, room_id, str(e))
            if msg_resp.status_code != 200 or psn_resp.status_code != 200: return __replyError__(key, room_id, 'recv message and person detail')
            
            try:
                msg_data = msg_resp.json()
                psn_data = psn_resp.json()
                recv_text = msg_data['text']
                person_name = psn_data['displayName']
            except Exception as e: return __replyError__(key, room_id, str(e))
            kv = re.match('^%s\s*(?P<text>.*)' % bot_name, recv_text)
            if kv:
                recv_text = kv.group('text')
                space = True
            else: space = False
            
            try: ret_text = func({'hook' : req.data,
                                  'person' : psn_data,
                                  'message' : msg_data,
                                  'room_id' : room_id,
                                  'person_id' : person_id,
                                  'space' : space},
                                 person_name,
                                 recv_text)
            except Exception as e: return __replyError__(key, room_id, str(e))
            
            if ret_text != None:
                if isinstance(ret_text, MarkDown):
                    try: send_text = __encoding_str__(ret_text.text)
                    except: return __replyError__(key, room_id, 'encode string')
                    if space:
                        to_msg = u'TO : %s' % person_name
                        try: requests.post(SPARK_MESSAGE_URL, headers=headers, json={'roomId' : room_id, 'text' : to_msg})
                        except: pass
                    try: resp = requests.post(SPARK_MESSAGE_URL, headers=headers,
                                              json={'roomId' : room_id,
                                                    'markdown' : send_text})
                    except Exception as e: return __replyError__(key, room_id, str(e))
                else:
                    try: send_text = __encoding_str__(ret_text)
                    except: return __replyError__(key, room_id, 'encode string')
                    if space:
                        send_text = u'To : %s\n%s' % (person_name, send_text)
                    try: resp = requests.post(SPARK_MESSAGE_URL, headers=headers,
                                              json={'roomId' : room_id,
                                                    'text' : send_text})
                    except Exception as e: return __replyError__(key, room_id, str(e))
                if resp.status_code != 200: return __replyError__(key, room_id, 'send message')
            return 'ok'
    
        return decofunc
    return botfunc