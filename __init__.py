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
from talkbox import TalkBox, Talk, Key

def listen(bot_key, bot_id, bot_name, bot_server):
    
    bot = Bot(bot_key, bot_id, bot_name, bot_server)
    
    def botfunc(func):
        
        @pygics.api('POST', '/sparkbot/' + bot_id)
        def decofunc(req, *argv, **kargs):
            try:
                message = Message(bot, req)
                message.reply(func(message, message.who, message.text))
            except Message.Bypass: pass
            except Exception as e: message.replyError(e)
            return 'ok'
    
        return decofunc
    
    return botfunc