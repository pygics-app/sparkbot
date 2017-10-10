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
            message = Message(bot, req)
            try: message.reply(func(message, message.who, message.text))
            except Exception as e: return message.replyError(e)
            return 'ok'
    
        return decofunc
    
    return botfunc