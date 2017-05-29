# -*- coding: utf-8 -*-
'''
Created on 2017. 4. 12.
@author: HyechurnJang
'''

import pygics
import sparkbot

BOT_ID = ''
BOT_KEY = ''
BOT_SERVER = ''

@pygics.api('POST', BOT_ID)
@sparkbot.message(BOT_KEY, BOT_ID, BOT_SERVER)
def episode(data, who, text):
    #===========================================================================
    # Write Code Here !
    #===========================================================================
    if text.lower() in ['hi', 'hello']:
        return 'Hello!'
    return '%s say that\n"%s"' % (who, text)