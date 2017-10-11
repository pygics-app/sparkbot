# -*- coding: utf-8 -*-
'''
Created on 2017. 4. 12.
@author: HyechurnJang
'''

from sparkbot import *

BOT_NAME = ''
BOT_ID = ''
BOT_KEY = ''
BOT_SERVER = ''

@listen(BOT_KEY, BOT_ID, BOT_NAME, BOT_SERVER)
def episode(msg, who, text):
    #===========================================================================
    # Write Code Here !
    #===========================================================================
    if text.lower() in ['hi', 'hello']:
        return 'Hello!'
    return '%s say that\n"%s"' % (who, text)