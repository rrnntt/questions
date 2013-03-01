import webapp2
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache
from mytemplate import write_template

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
    
    def nickname(self):
        """Return user nickname"""
        if self.user:
            return self.user.nickname()
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
     
    def __str__(self):
        """Print the user"""
        email = self.email()
        if not email:
            email = ''
        return '{'+self.nickname()+', '+email+'}'
    
def get_user(name):
    """Get user from datastore by nickname"""
    user = MyUser.get_by_key_name(name)
    return user

def create_user(name,roles, passwd = None):
    """Create a user with given nickname. 
    
    If user with this nickname already exists just return him/her.
    
    Args:
        name (str): Nickname for a user
        roles (list of str): roles for this user
    Return (MyUser):
        Created or existing user 
    """
    user = get_user(name)
    if not user:
        user = MyUser(key_name=name)
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
        #raise Exception('User '+name+' exists')
        user._nickname = name
    return user

def local_login(nickname,password):
    """Log in user without google account.
    
    Args:
        nickname (str): Nickname to login with
        passwd (str): User local password
    
    Return (MyUser):
        Logged in user or None if failed.
    """
    user = get_user(nickname)
    if not user or user.password() != password:
        return None
    memcache.add('local_user',user.key())
    return user
    
def local_logout():
    """Log out user without google account."""
    memcache.delete('local_user')
    
def get_current_user():
    """Return the current user if someone logged in or None otherwise"""
    default_user = 'test@example.com'
    gUser = users.get_current_user()
    if not gUser:
        user_key = memcache.get('local_user')
        if not user_key:
            return None
        user = MyUser.get(user_key)
    else:
        user = get_user(gUser.nickname())
    if user and not user.user:
        user.user = gUser 
    # if default user logged in but not registered - register him (me)
    if not user and gUser.nickname() == default_user:
        user = MyUser(key_name=default_user)
        user.user = gUser
        user.roles.append('admin')
        user.put()
    # temporary:
    if gUser and gUser.nickname() == default_user:
        user.roles = ['admin']
    return user

def check_loggedin(func):
    """Decorator for requests handlers wich must check that a user has logged in"""
    def check_loggedin_wrapper(self):
        user = get_current_user()
        if not user:
            self.redirect('/')
        func(self)
    return check_loggedin_wrapper

def get_current_admin():
    """Return the current user if someone logged in and is an admin or None otherwise"""
    user = get_current_user()
    if not user or not user.isAdmin():
        return None
    return user

def get_current_teacher():
    """Return the current user if someone logged in and is an admin or None otherwise"""
    user = get_current_user()
    if not user or not user.isTeacher():
        return None
    return user

#########################################################################
#    Request handlers
#########################################################################

class UserList(webapp2.RequestHandler):
    def get(self):

        user = get_current_admin()
        if not user:
            self.redirect('/')
        
        user_list = MyUser.all().fetch(1000)
            
        template_values = {
            'user_list': user_list,
        }
        write_template(self, user, 'user_list.html',template_values)
        
class DeleteUser(webapp2.RequestHandler):
    def post(self):
        encoded_key = self.request.get('key')
        key = db.Key(encoded=encoded_key)
        user = MyUser.get(key)
        if user:
            user.delete()
        self.redirect('/userlist')
        
class AddUser(webapp2.RequestHandler):
    def post(self):
        name = self.request.get('new-name')
        if len(name) > 0:
            create_user(name)
        self.redirect('/userlist')
        
