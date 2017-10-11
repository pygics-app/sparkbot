# -*- coding: utf-8 -*-
'''
Created on 2017. 4. 12.
@author: HyechurnJang
'''

import re
import types
import jzlib
import pygics

from models import Bot, Message
from talkbox import Context, Talk, Key

def listen(bot_key, bot_id, bot_name, bot_server):
    
    bot = Bot(bot_key, bot_id, bot_name, bot_server)
    
    def botfunc(func):
        
        @pygics.api('POST', '/' + bot_id)
        def decofunc(req, *argv, **kargs):
            try:
                msg = Message(bot, req)
                msg.reply(func(msg, msg.who, msg.text))
            except Message.Bypass: pass
            except Exception as e: msg.replyError(e)
    
        return decofunc
    
    return botfunc