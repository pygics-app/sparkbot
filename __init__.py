# -*- coding: utf-8 -*-
'''
Created on 2017. 4. 12.
@author: HyechurnJang
'''

import pygics
import requests

SPARK_WEBHOOK_URL = 'https://api.ciscospark.com/v1/webhooks/'
SPARK_MESSAGE_URL = 'https://api.ciscospark.com/v1/messages/'
SPARK_PERSON_URL = 'https://api.ciscospark.com/v1/people/'

def registerHook(key, name, url):
    headers = {'Content-type' : 'application/json; charset=utf-8', 'Authorization' : 'Bearer %s' % key}
    try:
        resp = requests.get(SPARK_WEBHOOK_URL, headers=headers)
        whs = resp.json()['items']
        isHook = False
        for wh in whs:
            if wh['name'] == name and wh['targetUrl'] == url: isHook = True
            else:
                try: requests.delete(SPARK_WEBHOOK_URL + wh['id'], headers=headers)
                except: pass
        if not isHook:
            resp = requests.post(SPARK_WEBHOOK_URL, headers=headers,
                                 json={'name' : name,
                                       'targetUrl' : url,
                                       'resource' : 'messages',
                                       'event' : 'created'})
            if resp.status_code == 200: return True
    except: return False
    return False

def replyError(key, room_id, err_msg='unknown error'):
    headers = {'Content-type' : 'application/json; charset=utf-8', 'Authorization' : 'Bearer %s' % key}
    try:
        requests.post(SPARK_MESSAGE_URL, headers=headers,
                      json={'roomId':room_id,
                            'text':'Ouch! I have error~~ d[X_X]b\n%s' % err_msg})
    except: return 'failed'
    return 'failed'

def message(key, bot_id, bot_server):
    
    registerHook(key, bot_id + 'Hook', 'http://%s/sparkbot/%s' % (bot_server, bot_id))
    bot_email = bot_id + '@sparkbot.io'
    
    def botfunc(func):
        def decofunc(req):
            try:
                req_data = req.data['data']
                msg_id = req_data['id']
                room_id = req_data['roomId']
                person_id = req_data['personId']
                person_email = req_data['personEmail']
            except: return 'failed'
            if person_email == bot_email: return 'bypass'
            
            headers = {'Content-type' : 'application/json; charset=utf-8', 'Authorization' : 'Bearer %s' % key}
            
            try:
                msg_resp, psn_resp = pygics.Burst(
                )(requests.get, SPARK_MESSAGE_URL + msg_id, headers=headers
                )(requests.get, SPARK_PERSON_URL + person_id, headers=headers
                ).do()
            except Exception as e: return replyError(key, room_id, str(e))
            if msg_resp.status_code != 200 or psn_resp.status_code != 200: return replyError(key, room_id, 'recv message and person detail')
            
            try:
                msg_data = msg_resp.json()
                psn_data = psn_resp.json()
                recv_text = msg_data['text']
                person_name = psn_data['displayName']
            except Exception as e: return replyError(key, room_id, str(e))
            
            try: ret_text = func({'hook' : req.data,
                                   'person' : psn_data,
                                   'message' : msg_data},
                                   person_name,
                                   recv_text)
            except Exception as e: return replyError(key, room_id, str(e))
            
            if ret_text != None:
                try: send_text = 'To: %s\n%s' % (person_name, ret_text)
                except:
                    try: send_text = 'To: %s\n%s' % (person_name, ret_text.decode('utf-8'))
                    except:
                        try: send_text = 'To: %s\n%s' % (person_name, ret_text.decode('utf-16'))
                        except: return replyError(key, room_id, 'encode string')
                try:
                    resp = requests.post(SPARK_MESSAGE_URL, headers=headers,
                                         json={'roomId' : room_id,
                                               'text' : send_text})
                except Exception as e: return replyError(key, room_id, str(e))
                if resp.status_code != 200: return replyError(key, room_id, 'send message')
            return 'ok'
    
        return decofunc
    return botfunc