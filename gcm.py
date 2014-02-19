import logging
import json
import urllib
import urllib2
  
def notifyDevices(device_ids):
    url = 'https://android.googleapis.com/gcm/send'
    headers = {'Content-Type' : 'application/json',
        'Authorization' : 'key=AIzaSyAQJeANrLytJwVMTWyeLq69BfQ-yrUV-Ns'}
    # get user device id
    values = {
        "registration_ids" : device_ids,
        "data" : { "msg" : "db-updated"}
    }

    req = urllib2.Request(url, json.dumps(values), headers)
    try:
        response = urllib2.urlopen(req)
        return True
    except urllib2.HTTPError as e:
        print e.code
        print e.read() 
        logging.info('HTTPError = ' + e.code)
        return False
