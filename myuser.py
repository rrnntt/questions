import webapp2
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache
import re
import random
import logging

logger = logging.getLogger('MyUser')

class MyUser(db.Model):
    """User of the system"""
    # google user
    user = db.UserProperty()
    # admin, teacher, student 
    roles = db.StringListProperty()
    _nickname = db.StringProperty()
    # password for user without google account
    _passwd = db.StringProperty()
    _first_name = db.StringProperty()
    _last_name = db.StringProperty()
    _email = db.StringProperty()
    _clss = db.ReferenceProperty()
    alias = db.StringProperty()
    
    def nickname(self):
        """Return user nickname"""
        if self.user:
            return self.user.nickname().lower()
        else:
            return self._nickname
        
    def password(self):
        """Return password if registered without google. Raise otherwise."""
        if self.user or self._passwd == '':
            raise Exception('Use google login')
        else:
            return self._passwd
        
    def email(self):
        """Return email"""
        if self._email:
            return self._email
        if self.user:
            return self.user.email()
        return None
    
    def set_email(self, email):
        """Set new email for all types of users"""
        self._email = email
        self.put()
        
    def isAdmin(self):
        """Check if user is admin"""
        return 'admin' in self.roles
     
    def isTeacher(self):
        """Check if user is teacher"""
        return 'teacher' in self.roles
     
    def isStudent(self):
        """Check if user is student"""
        return 'student' in self.roles
    
    def isLocal(self):
        """Check if user is local (not logged in with google)"""
        return self.user == None
    
    def set_role(self, role):
        if not role in self.roles:
            self.roles.append( role )
        self.put()
        
    def set_full_name(self, first_name, last_name):
        self._first_name = first_name
        self._last_name = last_name
        self.put()
        
    def first_name(self):
        return self._first_name
     
    def last_name(self):
        return self._last_name
     
    def full_name(self):
        fname = ''
        if self._first_name:
            fname += self._first_name
        if self._last_name:
            fname += ' ' + self._last_name
        return fname
    
    def set_class(self, clss):
        self._clss = clss.key()
        self.put()
        
    def from_json(self, model):
        logger.info(str(model))
        
        if 'nickname' in model:
            self._nickname = model['nickname'].lower()
        if 'roles' in model:
            roles = model['roles']
            if isinstance(roles,str) or isinstance(roles,unicode):
                self.roles = roles.split(',')
            else: 
                self.roles = roles
        
        if 'password' in model:
            self._passwd = model['password']
        if 'first_name' in model:
            self._first_name = model['first_name']
        if 'last_name' in model:
            self._last_name = model['last_name']
        if 'email' in model:
            self._email = model['email']
        if 'alias' in model:
            self.alias = model['alias']
        #if 'clss' in model:
        #    self._clss = db.Key(encoded=model['clss'])
        
     
    def __str__(self):
        """Print the user"""
        email = self.email()
        if not email:
            email = ''
        return self.nickname()
    
def get_unique_nickname():
    """Create unique student nickname of the form s1234"""
    query = MyUser.all().filter('roles =','student').order('_nickname')
    pattern = re.compile(r's(\d{4})')
    i = 1234
    for user in query.run():
        mo = pattern.match(user.nickname().lower())
        if mo:
            n = int(mo.group(1))
            if n > 0 and n - i > 1:
                new_name = 's' + str(i+1) 
                if get_user(new_name) == None:
                    return new_name
            i = n
    return 's' + str(i + 1)

def get_random_password():
    return '{:04}'.format( random.randint(101,9999) ) 
    
def get_user(nickname):
    """Get user from datastore by nickname"""
    user = MyUser.get_by_key_name(nickname.lower())
    return user

def create_user(name,roles = None, passwd = None):
    """Create a user with given nickname. 
    
    If user with this nickname already exists just return him/her.
    
    Args:
        name (str): Nickname for a user
        roles (list of str): roles for this user
    Return (MyUser):
        Created or existing user 
    """
    if roles == None:
        nickname = name['nickname'].lower()
    else:
        nickname = name.lower()
    user = get_user(nickname)
    if user == None:
        user = MyUser(key_name=nickname)
        if roles == None:
            user.from_json(name)
        else:
            user._nickname = name
            if roles:
                if isinstance(roles, list):
                    user.roles = roles
                else:
                    user.roles.append(roles)
            if passwd:
                user._passwd = passwd
        if user.alias == None or len(user.alias) == 0:
            user.alias = user.nickname() 
        logger.info('alias='+str(user.alias))
        user.put()
    else:
        raise Exception('User '+nickname+' exists')

    return user


def google_login(email,user_id):
    """Emulate google login for testing"""
    import os
    os.environ['USER_EMAIL']= email
    os.environ['USER_ID']= user_id
    #os.environ['FEDERATED_IDENTITY']= 'abc321'
    #os.environ['FEDERATED_PROVIDER']= '321'

