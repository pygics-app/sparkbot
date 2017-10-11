# -*- coding: utf-8 -*-
'''
Created on 2017. 9. 29.
@author: HyechurnJang
'''

from sparkbot import *

BOT_NAME = ''
BOT_ID = ''
BOT_KEY = ''
BOT_SERVER = ''

def answer_hello(msg):
    return u'%s님 안녕하세요' % msg.who

def answer_thank(msg):
    return u'별 말씀을요~\n%s님이 부르시면 언제든지 도와드릴게요' % msg.who

tb = Context(u'처리중입니다', u'에러가 발생했어요')(
    Talk('init', None, u'무슨 말씀인지 모르겠어요')(
        Key(
            [u'안녕', u'하이', u'헬로', u'반가', u'방가', u'hello', u'hi'],
            answer_hello
        ),
        Key(
            [u'선택', u'고름', u'골라', u'고를'],
            'select'
        ),
        Key(
            [u'부탁', u'도움', u'도와'],
            u'무엇을 도와드릴까요? 저는 "선택" 기능이 있어요'
        ),
        Key(
            [u'너', u'넌', u'누구', u'소개', u'정보'],
            u'저는 Spark Sample Bot 입니다'
        ),
        Key(
            [u'수고', u'고마', u'고맙', u'감사'],
            answer_thank
        ),
    ),
    Talk('select', u'사과와 배 중에 무엇을 좋아하세요?', u'사과 배 중에 선택하세요')(
        Key(
            u'사과',
            u'사과를 선택하셨습니다'
        ),
        Key(
            u'배',
            u'배를 선택하셨습니다'
        )
    )
)

@listen(BOT_KEY, BOT_ID, BOT_NAME, BOT_SERVER)
def episode(msg, who, text):
    #===========================================================================
    # Write Code Here !
    #===========================================================================
    
    return tb.do(msg)
