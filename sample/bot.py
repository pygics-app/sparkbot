# -*- coding: utf-8 -*-
'''
Created on 2017. 4. 12.
@author: HyechurnJang
'''

from sparkbot import *

BOT_NAME = '' # "Name" Field
BOT_USERNAME = '' # "Bot Username" Field without @sparkbot.io
BOT_KEY = '' # "Bot Access Token" Field
BOT_SERVER = '' # Pygics SparkBot Server IP and Port

@listen(BOT_KEY, BOT_ID, BOT_NAME, BOT_SERVER)
def episode(msg, who, text):
    #===========================================================================
    # Write Code Here !
    #===========================================================================
    if text.lower() in ['hi', 'hello']:
        return 'Hello!'
    return '%s say that\n"%s"' % (who, text)