# -*- coding: utf-8 -*-
'''
Created on 2017. 10. 10.
@author: HyechurnJang
'''

import re
import types
import pygics

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
            if reply != None and next_reply != None: return '%s\n%s' % (reply, next_reply)
            elif reply != None and next_reply == None: return reply
            elif reply == None and next_reply != None: return next_reply
        else: return self.locking