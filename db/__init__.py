from google.appengine.ext import db

OPTION_N = "0"
OPTION_Y = "1"

class Counter(db.Model):
    count = db.IntegerProperty(required=True, default=0)
    updated_time = db.DateTimeProperty(auto_now=True)   
    
    @staticmethod
    def getCount(key_name):
        c = Counter.get_by_key_name(key_name)
        count = 0
        if c:
            count = c.count
        return count
    
    @staticmethod 
    def inc(key_name):
        c = Counter.get_or_insert(key_name=key_name)
        c.count = c.count + 1
        c.put()
        return c.count

class User(db.Model):
    name = db.StringProperty()
    pwd = db.StringProperty()
    latest_sign_in_time = db.DateTimeProperty(auto_now=True)
    created_time = db.DateTimeProperty(auto_now=True)
    updated_time = db.DateTimeProperty(auto_now=True)

class Customer(db.Model):
    name = db.StringProperty(required=True)
    birthday = db.DateTimeProperty()
    birthdate = db.StringProperty()
    phone = db.PhoneNumberProperty()
    email = db.EmailProperty()
    note = db.TextProperty()
    msg_approval = db.BooleanProperty(default=False)
    deleted = db.BooleanProperty(default=False)
    created_time = db.DateTimeProperty(auto_now=True)   
    
    def tojson(self):
        birthday = ""
        phone = ""
        email = ""
        note = ""
        if self.birthday:
            birthday = self.birthday.strftime("%m/%d/%Y")
        if self.phone:
            phone = self.phone
        if self.email:
            email = self.email
        if self.note:
            note = self.note
        msg_approval = OPTION_Y if self.msg_approval else OPTION_N
        return {'name':self.name, 'birthday':birthday, 'phone':phone, 'email':email, 'key':str(self.key()), 'note':note, 'msg_approval':msg_approval}

class Tag(db.Model):
    name = db.StringProperty(required=True)
    type = db.IntegerProperty(required=True)
    
    TYPE_ITEM = 1
    TYPE_CUSTOMER = 2
    
    def tojson(self):
        return {'name':self.name, 'key':str(self.key()) }
    
class Item(db.Model):
    name = db.StringProperty(required=True)
    tags = db.ListProperty(db.Key, default=None)
    created_time = db.DateTimeProperty(auto_now=True)
    
    def tojson(self, withTags=True):
        return {'name':self.name,'tags':None, 'key':str(self.key()) }
    
"""class Room(db.Model):
    name = db.StringProperty(required=True)
    floor = db.IntegerProperty(default=0)
    created_time = db.DateTimeProperty(auto_now=True)
    
    def tojson(self):
        return {'name':self.name,'floor':self.floor, 'key':str(self.key()) }"""
    
class Reserve(db.Model):
    customer = db.ReferenceProperty(Customer, required=True)
    date_from = db.DateTimeProperty(required=True)   
    date_to = db.DateTimeProperty(required=True)   
    item = db.ReferenceProperty(Item, required=True)
    breakfast = db.IntegerProperty(default=0)
    paid = db.IntegerProperty(required=True, default=0)
    """
    RESERVE_STATUS_NORMAL = 0
    RESERVE_STATUS_CANCELLED = 2
    RESERVE_STATUS_DELETED = 3
    """
    status = db.IntegerProperty(required=True, default=0)
    note = db.TextProperty()
    created_time = db.DateTimeProperty(auto_now=True)
    
    def tojson(self):
        customer = self.customer.tojson()
        item = self.item.tojson()
        return {
                    'customer':customer,
                    'item':item,
                    'date_from':self.date_from.strftime("%m/%d/%Y"),
                    'date_to':self.date_to.strftime("%m/%d/%Y"),
                    'breakfast':self.breakfast,
                    'paid':self.paid,
                    'status':self.status,
                    'note':self.note,
                    'key':str(self.key())
                }
    
class Task(db.Model):
    content = db.StringProperty(required=True)
    finished = db.BooleanProperty(default=False)
    cleared = db.BooleanProperty(default=False)
    created_time = db.DateTimeProperty(auto_now=True)
    
    def tojson(self):
        return { 'key':str(self.key()), 'content':self.content, 'finished':self.finished }