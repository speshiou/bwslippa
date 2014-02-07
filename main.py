#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import json

import logging

from google.appengine.ext.db import *

from datetime import datetime,timedelta

from google.appengine.api import users

from webapp2_extras import sessions

from db import *

import webapp2 as webapp
from django import template
from django.conf import settings
settings.configure(DEBUG=True)

RESERVE_STATUS_NORMAL = 0
RESERVE_STATUS_CANCELLED = 2
RESERVE_STATUS_DELETED = 3

RESERVE_PAID_N = 0
RESERVE_PAID_Y = 1

OPTION_N = "0"
OPTION_Y = "1"

KEY_COUNTER_CUSTOMER_COUNT = "key_counter_customer"
KEY_SESSION_USER = "key_session_user"

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}


class MainHandler(webapp.RequestHandler):
    def get(self):
        template_values = {
                "app_name":"BWSLIPPA HOSTEL",
                "years":range(datetime.today().year, datetime.today().year - 100, -1),
                "months":range(1, 13),
                "days":range(1, 32),
                "locale":"zh-TW"
            }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        t = template.Template(file(path,'rb').read())
        self.response.out.write(t.render(template.Context(template_values)))
        
class CssHandler(webapp.RequestHandler):
    def get(self):
        ##2186D8
        #2E6E9E
        #1447BE
        #0065B7
        #0072c6
        template_values = {
            'header':'#0072c6'
            }

        path = os.path.join(os.path.dirname(__file__), 'templates/css/default.css')
        t = template.Template(file(path,'rb').read())
        self.response.headers['Content-Type'] = 'text/css'
        self.response.out.write(t.render(template.Context(template_values)))

class Balance(webapp.RequestHandler):
    def get(self):
        date = self.request.get('d')
        q = Reserve.all()
        q.filter('status =', RESERVE_STATUS_NORMAL)
        if date and date != 'all':
            q.filter('date_from <=', datetime.strptime(date, "%m/%d/%Y"))
        elif date == 'all':
            pass
        else:
            q.filter('date_from <=', datetime.today())
            
        count = q.count()
        total = 0
        for r in q:
            if "3" in r.item.name:
                total += 2001
            else:
                total += 1200
        self.response.out.write("reserved:%d, total:%d" % (count, total))
        

class ExportXls(webapp.RequestHandler):
    def get(self):
        date = self.request.get('now')
        date = datetime.strptime(date, "%m/%d/%Y")
        items = Item.all()
        html = """<html xmlns="http://www.w3.org/1999/xhtml">
                    <head>
                    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
                    </head>
                    <body><table style='font-size:14px;border-width: 1px;' border='1'>"""
        html += "<tr><th>Room</th><th>Name</th><th>Birthday</th><th>Phone</th><th>Email</th><th>From</th><th>To</th><th>Breakfast</th><th>Paid</th><th>Note</th></tr>"
        for item in items:
            q = Reserve.all()
            q.filter('status =', RESERVE_STATUS_NORMAL)
            q.filter('item =', item)
            q.filter('date_from <=', date)
            q.order('-date_from')
            r = q.fetch(10)
            customer_name = ""
            birthday = ""
            phone = ""
            email = ""
            date_from = ""
            date_to = ""
            breakfast = 0
            paid = "No"
            note = ""
            for reserve in r:
                if reserve.date_from <= date and reserve.date_to >= date:
                    customer_name = reserve.customer.name
                    date_from = reserve.date_from.strftime("%m/%d/%Y")
                    date_to = reserve.date_to.strftime("%m/%d/%Y")
                    note = reserve.note
                    if reserve.customer.birthday:
                        birthday = reserve.customer.birthday.strftime("%m/%d/%Y")
                    if reserve.customer.phone:
                        phone = reserve.customer.phone
                        phone += "'"
                    if reserve.customer.email:
                        email = reserve.customer.email
                    if reserve.breakfast:
                        breakfast = reserve.breakfast
                    if reserve.paid:
                        paid = 'Yes' if reserve.paid == RESERVE_PAID_Y else 'No'
            html += """<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>
                    """ % (item.name, customer_name, birthday, phone, email, date_from, date_to, str(breakfast), paid, note) 

        html += "</table></body></html>"
        self.response.headers['Content-Type'] = "application/vnd.ms-execl;charset=utf-8" 
        self.response.headers['Content-Disposition'] = str("attachment; filename=%s.xls"%date.strftime("%Y%m%d")) 
        self.response.headers['Pragma'] = "no-cache" 
        self.response.headers['Expires'] = "0" 
        self.response.out.write(html)
        

        
"""class ItemCreateHandler(webapp.RequestHandler):
    def get(self):
        q = Room.all()
        rooms = q.fetch(q.count())
        for r in rooms:
            tagname = "%dF" % (r.floor)
            q = Tag.all()
            q.filter('name =', tagname)
            q.filter('type =', Tag.TYPE_ITEM)
            if(q.count() > 0):
                tag = q.fetch(1)[0]
            else:
                tag = Tag(name = tagname, type=Tag.TYPE_ITEM)
                tag.put()
                
            itemname = r.name
            q = Item.all()
            q.filter('name =', itemname)
            if(q.count() > 0):
                item = q.fetch(1)[0]
            else:
                item = Item(name = itemname)
                item.tags = [tag.key()]
                item.put()
                
            q = Reserve.all()
            q.filter('room =', r)
            records = q.fetch(q.count())
            for record in records:
                record.item = item
            db.put(records)"""
            
class Birthdate(webapp.RequestHandler):
    def get(self):
        q = Customer.all()
        q.filter('birthday !=', None)
        updated = []
        for r in q:
            if r.birthday:
                r.birthdate = r.birthday.strftime("%m/%d")
                updated.append(r)
                logging.debug(r.birthdate)
        db.put(updated)
        self.response.out.write("%d updated" % (len(updated)))

class MergeCustomers(webapp.RequestHandler):
    def get(self):
        customers = Customer.all()
        customers.order("name")
        lastCustomer = None
        i = 0
        for c in customers:
            if not lastCustomer:
                lastCustomer = c
                continue
            if c.name == lastCustomer.name and c.phone == lastCustomer.phone:
                records = Reserve.all()
                records.filter("customer = ", c.key())
                for r in records:
                    i += 1
                    r.customer.deleted = True
                    r.customer.put()                  
                    r.customer = lastCustomer
                    r.put()
                continue
            lastCustomer = c
        self.response.out.write("merge %d customers"%(i))
        
class SearchHandler(webapp.RequestHandler):
    def get(self):
        keyword = self.request.get('query')
        if not keyword:
            self.response.out.write(json.dumps([])) 
        q = db.GqlQuery("SELECT * FROM Customer WHERE name >= :1 AND name < :2", keyword, keyword + u"\ufffd ORDER BY name ASC")
        results = q.fetch(30)
        suggestions = []
        data = []
        for r in results:
            if r.deleted:
                continue
            birthday = ""
            phone = ""
            email = ""
            label = r.name
            if r.birthday:
                birthday = r.birthday.strftime("%m/%d/%Y")
            if r.phone:
                phone = r.phone
                label += " (%s)" % (phone)
            if r.email:
                email = r.email
            msg_approval = OPTION_Y if r.msg_approval else OPTION_N
            suggestions.append(label)
            data.append({'name':r.name, 'key':str(r.key()), 'isItem':False})

        if not len(suggestions):
            q = db.GqlQuery("SELECT * FROM Customer WHERE phone >= :1 AND phone < :2", keyword, keyword + u"\ufffd ORDER BY name ASC")
            results = q.fetch(30)
            ret = []
            for r in results:
                if r.deleted:
                    continue
                birthday = ""
                phone = ""
                email = ""
                label = r.name
                if r.birthday:
                    birthday = r.birthday.strftime("%m/%d/%Y")
                if r.phone:
                    phone = r.phone
                    label += " (%s)" % (phone)
                if r.email:
                    email = r.email
                msg_approval = OPTION_Y if r.msg_approval else OPTION_N
                suggestions.append(label)
                data.append({'name':r.name, 'key':str(r.key()), 'isItem':False})

        q = db.GqlQuery("SELECT * FROM Item WHERE name >= :1 AND name < :2", keyword, keyword + u"\ufffd ORDER BY floor DESC")
        for r in q:
            suggestions.append(r.name)
            data.append({'name':r.name, 'key':str(r.key()), 'isItem':True})

        self.response.out.write(json.dumps({ 'query':keyword, 'suggestions':suggestions, 'data':data }))
        
class QueryCustomer(webapp.RequestHandler):
    def get(self): 
        keyword = self.request.get('term')
        q = db.GqlQuery("SELECT * FROM Customer WHERE name >= :1 AND name < :2", keyword, keyword + u"\ufffd ORDER BY name ASC")
        results = q.fetch(30)
        ret = []
        for r in results:
            if r.deleted:
                continue
            birthday = ""
            phone = ""
            email = ""
            label = r.name
            if r.birthday:
                birthday = r.birthday.strftime("%m/%d/%Y")
            if r.phone:
                phone = r.phone
                label += " (%s)" % (phone)
            if r.email:
                email = r.email
            msg_approval = OPTION_Y if r.msg_approval else OPTION_N
            ret.append({'name':r.name, 'key':str(r.key()), 'label':label, 'birthday':birthday, 'phone':phone, 'email':email, 'msg_approval':msg_approval})
        if not len(ret):
            q = db.GqlQuery("SELECT * FROM Customer WHERE phone >= :1 AND phone < :2", keyword, keyword + u"\ufffd ORDER BY name ASC")
            results = q.fetch(30)
            ret = []
            for r in results:
                if r.deleted:
                    continue
                birthday = ""
                phone = ""
                email = ""
                label = r.name
                if r.birthday:
                    birthday = r.birthday.strftime("%m/%d/%Y")
                if r.phone:
                    phone = r.phone
                    label += " (%s)" % (phone)
                if r.email:
                    email = r.email
                msg_approval = OPTION_Y if r.msg_approval else OPTION_N
                ret.append({'name':r.name, 'key':str(r.key()), 'label':label, 'birthday':birthday, 'phone':phone, 'email':email, 'msg_approval':msg_approval})
        self.response.out.write(json.dumps(ret))   
        
class QueryItems(webapp.RequestHandler):
    def get(self): 
        keyword = self.request.get('term')
        q = db.GqlQuery("SELECT * FROM Item WHERE name >= :1 AND name < :2", keyword, keyword + u"\ufffd ORDER BY floor DESC")
        ret = []
        for r in q:
            ret.append({'name':r.name, 'key':str(r.key()), 'label':r.name})
        self.response.out.write(json.dumps(ret))      
    
class AddApp(webapp.RequestHandler):
    def get(self): 
        self.response.out.write('AddApp') 
           

class BaseHandler(webapp.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
        try:
            # Dispatch the request.
            webapp.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

           
class Signup(BaseHandler):
    def get(self): 
        cuser = users.get_current_user()
        if cuser:
            user = User.get_by_key_name(cuser.email())
            if not user:
                mail = cuser.email()
                user = User(key_name=mail, name=mail, pwd='')
                user.put()
            
            self.session[KEY_SESSION_USER] = user.key().name()   
            self.redirect("/addapp") 
        else:
            self.redirect("/welcome") 
        
            
class Welcome(webapp.RequestHandler):
    def get(self): 
        cuser = users.get_current_user()
        if cuser:
            user = User.get_by_key_name(cuser.email())
            if user:
                self.redirect("/") 
                return

        login = ('Welcome! (<a href="%s">Start</a>)' % (users.create_login_url('/signup')))
        self.response.out.write(login)   

        
class CustomerCounter(webapp.RequestHandler):
    def get(self): 
        q = Customer.all()
        q.filter("deleted =", False)
        count = 0
        for r in q:
            count = count + 1
        c = Counter.get_or_insert(key_name=KEY_COUNTER_CUSTOMER_COUNT)
        c.count = count
        c.put()
        
class CreateTestData(webapp.RequestHandler):
    def get(self): 
        for i in range(1, 6):
            tag = Tag(name="%dF" % (i), type=Tag.TYPE_ITEM)
            tag.put()
            for j in range(1, 6):
                item = Item(name="%d0%d" % (i, j))
                item.tags = [tag.key()]
                item.put()
                
 
class RPCHandler(BaseHandler):
    """ Allows the functions defined in the RPCMethods class to be RPCed."""
    def __init__(self, request, response):
        self.initialize(request, response)
        self.methods = RPCMethods()

    def get(self):
        func = None
   
        action = self.request.get('action')
        if action:
            if action[0] == '_':
                self.error(403) # access denied
                return
            else:
                func = getattr(self.methods, action, None)
   
        if not func:
            self.error(404) # file not found
            return
     
        args = ()
        while True:
            key = 'arg%d' % len(args)
            val = self.request.get(key)
            if val:
                args += (json.loads(val),)
            else:
                break
        result = func(*args)
        self.response.out.write(json.dumps(result))
        
    def post(self):
        args = json.loads(self.request.body)
        func, args = args[0], args[1:]
   
        if func[0] == '_':
            self.error(403) # access denied
            return
     
        func = getattr(self.methods, func, None)
        if not func:
            self.error(404) # file not found
            return

        result = func(*args)
        self.response.out.write(json.dumps(result))        

class RPCMethods:
    """ Defines the methods that can be RPCed.
    NOTE: Do not allow remote callers access to private/protected "_*" methods.
    """

    def Add(self, *args):
        # The JSON encoding may have encoded integers as strings.
        # Be sure to convert args to any mandatory type(s).
        ints = [int(arg) for arg in args]
        return sum(ints)
        
    def keepConn(self):
        # The JSON encoding may have encoded integers as strings.
        # Be sure to convert args to any mandatory type(s).
        return True        
        
    def item(self, isNew, key, name, tags):
        if isNew:
            item = Item(name=name.strip())
        else:
            item = db.get(db.Key(key))
            item.name = name.strip()
        item.tags = tags
        item.put()
        return {'success':True}
        
    def reserve(self, isNew, key, isNewCustomer, name, birthday, phone, email, msg_approval, date_from, date_to, item_key, breakfast, paid, note):
        date_from = datetime.strptime(date_from.strip(), "%m/%d/%Y")
        date_to = datetime.strptime(date_to.strip(), "%m/%d/%Y")
        if date_from > date_to:
            return { 'success':False, 'msg':"date_from > date_to" }
            
        if not isNew:    
            reserved = db.get(db.Key(key))    
            if not reserved:
                return {'success':False, 'msg':"no such record"}
            
        q = Reserve.all()
        q.filter("item =", db.Key(item_key))
        q.filter('status =', RESERVE_STATUS_NORMAL)
        q.filter("date_from >=", date_from)
        q.filter("date_from <=", date_to)
        if isNew and q.count() > 0:
            return { 'success':False, 'msg':"date_from occupied" }
        elif not isNew:
            for r in q:
                if r.key() != reserved.key():
                    return { 'success':False, 'msg':"date_from occupied" }
                    
        q = Reserve.all()
        q.filter("item =", db.Key(item_key))
        q.filter('status =', RESERVE_STATUS_NORMAL)
        q.filter("date_to >=", date_from)
        q.filter("date_to <=", date_to)
        if isNew and q.count() > 0:
            return { 'success':False, 'msg':"date_to occupied" } 
        elif not isNew:
            for r in q:
                if r.key() != reserved.key():
                    return { 'success':False, 'msg':"date_to occupied" } 
            
        if isNewCustomer:
            c = Customer(name=name.strip())
            Counter.inc(KEY_COUNTER_CUSTOMER_COUNT)
        else:
            c = db.get(db.Key(name))
        if phone.strip():
            c.phone = phone.strip()
        if email.strip():
            c.email = email.strip()
        if birthday.strip():
            c.birthday = datetime.strptime(birthday.strip(), "%m/%d/%Y")
            c.birthdate = c.birthday.strftime("%m/%d")
        c.msg_approval = True if str(msg_approval) == OPTION_Y else False
        c.put()
        if isNew:
            reserved = Reserve(customer=c, 
                date_from=date_from,
                date_to=date_to,
                item=db.get(db.Key(item_key)))
        else:
            reserved.customer = c
            reserved.date_from=date_from
            reserved.date_to=date_to
            reserved.item=db.get(db.Key(item_key))
        reserved.breakfast = int(breakfast)
        reserved.paid = int(paid)
        reserved.note = note
        reserved.put()
        return {'success':True}
        
    def customer(self, isNew, key, name, birthday, phone, email, msg_approval, note):
        if isNew:
            c = Customer(name=name.strip())
            Counter.inc(KEY_COUNTER_CUSTOMER_COUNT)
        else:
            c = db.get(db.Key(key))
            c.name = name.strip()
        if not c:
            return {'success':False}
        if phone.strip():
            c.phone = phone.strip()
        if email.strip():
            c.email = email.strip()
        if birthday.strip():
            c.birthday = datetime.strptime(birthday.strip(), "%m/%d/%Y")
            c.birthdate = c.birthday.strftime("%m/%d")
        c.msg_approval = True if str(msg_approval) == OPTION_Y else False
        c.note = note.strip()
        c.put()
        return {'success':True, 'result':c.tojson()}  
        
    def cancelReserved(self, key):
        reserve = db.get(db.Key(key))
        if reserve:
            reserve.status = RESERVE_STATUS_CANCELLED
            reserve.put()
            return {'success':True}
        return {'success':False}  
        
    def getItems(self):
        q = Item.all()
        q.order('name')
        items = [r.tojson() for r in q];
        return {'items':items}

    def queryItemInfo(self, key):
        item = db.get(db.Key(key))
        if not item:
            return {'success':False} 
        else:
            q = Reserve.all()
            q.filter("item =", item)
            q.filter('status =', RESERVE_STATUS_NORMAL)
            q.order('-date_to')
            result = [r.tojson() for r in q]
        
            return {'success':True, 'result':result, 'item':item.tojson() } 
            
  
    def getCustomerCount(self):
        count = Counter.getCount(KEY_COUNTER_CUSTOMER_COUNT)
        return {'count':count}
        
    def getCustomerReservedRecords(self, key):
        customer = db.get(db.Key(key))
        if customer:
            q = Reserve.all()
            q.filter("customer =", customer.key())
            q.order("-date_from")
            reserved = [r.tojson() for r in q]
            
            c = customer.tojson()
            return {'success':True, 'result':reserved, 'customer':c }     
        return {'success':False}
        
    def getReservedInfo(self, key):
        r = db.get(db.Key(key))
        if not r:
            return {'success':False}

        return {'success':True, 'result':r.tojson() }
        
    def queryBirthdays(self, date):
        date = datetime.strptime(date, "%m/%d/%Y")
        q = Customer.all()
        q.filter('birthdate =', date.strftime("%m/%d"))
        result = [r.tojson() for r in q]
        return {'success':True, 'result':result }
        
    def queryCustomerActivities(self):
        q = Reserve.all()
        q.order('-created_time')
        result = q.fetch(50)
        ret = []
        for r in result:
            ret.append(r.tojson())
        return { 'success':True, 'result':ret }
        
        
    def getReserved(self, date):
        items = Item.all()
        result = []
        if date:
            date = datetime.strptime(date, "%m/%d/%Y")
        else:
            date = datetime.today()
        for item in items:
            q = Reserve.all()
            q.filter('status =', RESERVE_STATUS_NORMAL)
            q.filter('item =', item)
            q.filter('date_to >=', date)
            q.order('date_to')
            reserve = q.fetch(1)
            records = []
            if len(reserve) > 0:
                reserve = reserve[0]
                if reserve.date_from <= date and reserve.date_to >= date:
                    records.append(reserve.tojson()) 
            if len(records) > 0:
                result.append({  'item':item.tojson(), 'records':records})
        return {'result':result, 'date':date.isoformat(' ')}
        
    def bindWorkspace(self):
        q = Tag.all()
        q.filter('type =', Tag.TYPE_ITEM)
        q.order('-name');
        tags = q.fetch(q.count())
        result = []
        for tag in tags:
            q = Item.all()
            q.filter('tags =', tag)
            q.order('name')
            items = [r.tojson() for r in q]
            result.append({'tag':tag.tojson(), 'items':items})
        return {'result':result }
        
    def getCustomer(self, key):
        c = db.get(db.Key(key))
        if c:
            return {'success':True, 'result':c.tojson() }
        return {'success':False}
        
    def todo(self, isNew, key, content, finished):
        if not content.strip():
            return { 'success':False }
        if(isNew):
            t = Task(content=content.rstrip())
        else:
            t = db.get(db.Key(key))
            t.content = content.rstrip()
        t.finished = finished
        t.put()
        return {'success':True, 'task':t.tojson() }
        
    def removeTask(self, key):
        t = db.get(db.Key(key))
        if t:
            t.delete()
        
    def queryTasks(self):
        q = Task.all()
        q.filter("cleared =", False)
        q.order("created_time")
        result = [r.tojson() for r in q]
        return { 'result':result }
        
    def clearFinishedTasks(self):
        q = Task.all()
        q.filter("cleared =", False)
        q.filter("finished =", True)
        updated = []
        for r in q:
            r.cleared = True
            updated.append(r)
        db.put(updated)
        return {'success':True}
        
    def getTimelineEvent(self, key, date):
        if date:
            date = datetime.strptime(date.strip(), "%m/%d/%Y")
        item = db.get(db.Key(key))
        if not item:
            return {'success':False} 
        else:
            q = Reserve.all()
            q.filter("item =", item)
            q.filter('status =', RESERVE_STATUS_NORMAL)
            if date:
                q.filter('date_to <=', date)
            q.order('-date_to')
            q.fetch(20)
            result = [r.tojson() for r in q]
        return {'success':True, 'result':result, 'item':item.tojson() } 
        
        
    def addOrUpdateTagName(self, tagKey, tagName): 
        if tagKey: # update
            tag = db.get(db.Key(tagKey))
            if not tag:
                return {'success':False} 
            else:
                tag.name = tagName
                tag.put()
                return {'success':True} 
        else: # add
            tag = Tag(name=tagName, type=Tag.TYPE_ITEM)
            tag.put()
            return {'success':True} 
            
            
    def deleteTagByKey(self, tagKey): 
        if tagKey: # update
            try:
                tag = db.get(db.Key(tagKey))
                if not tag:
                    return {'success':False} 
                else:
                    tag.delete()
                    return {'success':True} 
            except BadKeyError:
                logging.info('BadKeyError')
        else: # add
            return {'success':False} 
            
            
    def updateTagPriority(self, tagInfo): 
        if tagInfo: 
            try:
                updated = []
                logging.info(tagInfo)
                for o in tagInfo:
                    k = o['key']
                    p = o['priority']
                    tag = db.get(db.Key(k))
                    if tag:
                        tag.priority = p
                    
                    updated.append(tag)
                
                db.put(updated)
                return {'success':True} 
            except BadKeyError:
                logging.info('BadKeyError')
                return {'success':False} 
        else: 
            return {'success':False} 
            
     
    def processAddApp(self, expire_date, ap_name): 
        # user
        key = self.session.get(KEY_SESSION_USER)                
        user = User.get_by_key_name(key)
        # ap
        time = datetime.strptime(expire_date, "%m/%d/%Y")
        ap = AppInfo(name=ap_name)
        ap.expire_time=time
        ap.put()
        # match    
        match = AccountMatch(user=user, ap=ap)
        match.put()
        return {'success':True} 
            

app = webapp.WSGIApplication([('/', MainHandler),
                                          ('/_cron/customer_counter', CustomerCounter),
                                          ('/rpc', RPCHandler),
                                          ('/css', CssHandler),
                                          ('/customer', QueryCustomer),
                                          ('/item', QueryItems),
                                          ('/welcome', Welcome),
                                          ('/addapp', AddApp),
                                          ('/signup', Signup),
                                          ('/search', SearchHandler),
                                          ('/test', CreateTestData),
                                          ('/birthdate', Birthdate),
                                          ('/exportXls', ExportXls),
                                          ('/balance', Balance)],
                                         config=config,
                                         debug=True)
