import webapp2
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache
import re

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
        return self._first_name + ' '  + self._last_name
    
    def set_class(self, clss):
        self._clss = clss.key()
        self.put()
        
    def from_json(self, model):
        if 'nickname' in model:
            self._nickname = model['nickname'].lower()
        else:
            raise Exception('Model doesn\'t have nickname.')
        if 'roles' in model:
            roles = model['roles'].split(',')
            self.roles = roles
        else:
            raise Exception('Roles is missing form model.')
        if 'password' in model:
            self._passwd = model['password']
        if 'first_name' in model:
            self._first_name = model['first_name']
        if 'last_name' in model:
            self._last_name = model['last_name']
        if 'email' in model:
            self._email = model['email']
        #if 'clss' in model:
        #    self._clss = db.Key(encoded=model['clss'])
        
     
    def __str__(self):
        """Print the user"""
        email = self.email()
        if not email:
            email = ''
        return '{'+self.nickname()+', '+email+'}'
    
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
    
def get_user(name):
    """Get user from datastore by nickname"""
    user = MyUser.get_by_key_name(name.lower())
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
        user.put()
    else:
        raise Exception('User '+nickname+' exists')

    return user

def local_login(nickname,password):
    """Log in user without google account.
    
    Args:
        nickname (str): Nickname to login with
        passwd (str): User local password
    
    Return (MyUser):
        Logged in user or None if failed.
    """
    user = get_user(nickname.lower())
    if not user or user.password() != password:
        return None
    memcache.add('local_user',user.key())
    return user
    
def local_logout():
    """Log out user without google account."""
    memcache.delete('local_user')
    
def get_current_user():
    """Return the current user if someone logged in or None otherwise"""
    default_user = 'roman.tolchenov'
    gUser = users.get_current_user()
    if not gUser:
        #return MyUser(key_name=default_user)
        user_key = memcache.get('local_user')
        if not user_key:
            return None
        user = MyUser.get(user_key)
    else:
        user = get_user(gUser.nickname().lower())
    if user and not user.user:
        user.user = gUser 
    # if default user logged in but not registered - register him (me)
    if not user and gUser.nickname().lower() == default_user:
        user = MyUser(key_name=default_user)
        user.user = gUser
        user.roles = ['admin','teacher']
        user.put()
    # temporary:
#    if gUser and gUser.nickname() == default_user:
#        user.roles = ['admin','teacher']
    return user

def check_loggedin(func):
    """Decorator for requests handlers wich must check that a user has logged in"""
    def check_loggedin_wrapper(self):
        user = get_current_user()
        if not user:
            self.redirect('/')
            return
        func(self)
    return check_loggedin_wrapper

def get_current_admin():
    """Return the current user if someone logged in and is an admin or None otherwise"""
    user = get_current_user()
    if not user or not user.isAdmin():
        return None
    return user

def get_current_teacher():
    """Return the current user if someone logged in and is a teacher or None otherwise"""
    user = get_current_user()
    if not user or not user.isTeacher():
        return None
    return user

def get_current_student():
    """Return the current user if someone logged in and is a student or None otherwise"""
    user = get_current_user()
    if not user or not user.isStudent():
        return None
    return user

def google_login(email,user_id):
    """Emulate google login for testing"""
    import os
    os.environ['USER_EMAIL']= email
    os.environ['USER_ID']= user_id
    #os.environ['FEDERATED_IDENTITY']= 'abc321'
    #os.environ['FEDERATED_PROVIDER']= '321'

