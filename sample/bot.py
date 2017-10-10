# -*- coding: utf-8 -*-
'''
Created on 2017. 4. 12.
@author: HyechurnJang
'''

import sparkbot

BOT_NAME = ''
BOT_ID = ''
BOT_KEY = ''
BOT_SERVER = ''

@sparkbot.listen(BOT_KEY, BOT_ID, BOT_NAME, BOT_SERVER)
def episode(message, who, text):
    #===========================================================================
    # Write Code Here !
    #===========================================================================
    if text.lower() in ['hi', 'hello']:
        return 'Hello!'
    return '%s say that\n"%s"' % (who, text)