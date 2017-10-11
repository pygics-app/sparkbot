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
            keys = []
            ref = pattern
            while True:
                kv = re.search('{{(?P<key>\w+):.*}}', ref)
                if kv:
                    key = kv.group(1)
                    keys.append(kv.group(1))
                    ref = ref.replace('{{%s:' % key, '')
                else: break
            if keys:
                ref = pattern
                for key in self.keys: ref = ref.replace('{{%s:' % key, '(?P<%s>' % key)
                self.pattern = re.compile(ref.replace('}}', ')'), re.UNICODE)
                self.mtype = True
                self.keys = keys
            else:
                self.pattern = re.compile(pattern, re.UNICODE)
                self.mtype = False
        
        def match(self, msg):
            if self.mtype:
                result = {}
                kv = self.pattern.match(msg.text)
                if kv:
                    for key in self.keys: result[key] = unicode(kv.group(key))
                return result
            else:
                return True if self.pattern.search(msg.text) else False
    
    def __init__(self, patterns, action, next_id=None):
        if not isinstance(patterns, list): patterns = [patterns]
        self.patterns = []
        for pattern in patterns: self.patterns.append(Key.Pattern(pattern))
        self.action = action
        self.next_id = next_id
        
    def match(self, msg):
        for pattern in self.patterns:
            result = pattern.match(msg)
            if result: return pattern.original, result
        return None, None

class Talk:
    
    def __init__(self, id, init=None, dismatch=None, rewind=True):
        self.id = id
        self.init = init
        self.dismatch = dismatch
        self.rewind = rewind
        self.keys = []
    
    def __call__(self, *keys): return self.set(*keys)
    
    def set(self, *keys):
        for key in keys:
            if isinstance(key, Key): self.keys.append(key)
            else: raise Exception('incorrect key type')
        return self
    
    def getInit(self, msg):
        if isinstance(self.init, types.FunctionType): return self.init(msg)
        else: return self.init
    
    def getDismatch(self, msg):
        if isinstance(self.dismatch, types.FunctionType): return self.dismatch(msg)
        else: return self.dismatch
        
    def do(self, msg):
        for key in self.keys:
            match, result = key.match(msg)
            if result:
                if isinstance(key.action, types.FunctionType):
                    if isinstance(result, dict): reply = key.action(msg, **result)
                    else: reply = key.action(msg)
                else: reply = key.action
                msg.hist.append({'id' : self.id, 'text' : msg.text, 'key' : match, 'result' : result, 'reply' : reply})
                return reply, key.next_id
        if self.rewind: return self.getDismatch(msg), self.id
        else: return self.getDismatch(msg), None

class Context:
    
    def __init__(self, lock=None, error=None):
        self.lock = lock
        self.error = error
        self.talk = {}
        self.context = {}
        self.init = None
    
    def __call__(self, *keys): return self.set(*keys)
    
    def set(self, *talks):
        for talk in talks:
            if not self.init: self.init = talk
            self.talk[talk.id] = talk
        return self
    
    def getLock(self, msg):
        if isinstance(self.lock, types.FunctionType): return self.lock(msg)
        else: return self.lock
    
    def getError(self, msg):
        if isinstance(self.error, types.FunctionType): return self.error(msg)
        else: return self.error
    
    def do(self, msg):
        if msg.person_id not in self.context:
            self.context[msg.person_id] = {'curr' : self.init, 'hist' : [], 'lock' : pygics.Lock()}
        uref = self.context[msg.person_id]
        msg.curr = uref['curr']
        msg.hist = uref['hist']
        msg.lock = uref['lock']
        if msg.lock.acquire(False):
            try:
                reply, next_id = msg.curr.do(msg)
                if next_id != None and next_id != self.init.id:
                    next = self.talk[next_id]
                else:
                    next = self.init
                    uref['hist'] = []
                uref['curr'] = next
                next_reply = next.getInit(msg)
            except Exception as e:
                reply = self.getError(msg)
                next_reply = str(e)
            msg.lock.release()
            if reply != None and next_reply != None: return '%s\n%s' % (reply, next_reply)
            elif reply != None and next_reply == None: return reply
            elif reply == None and next_reply != None: return next_reply
        else: return self.getLock(msg)