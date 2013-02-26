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
    first_name = db.StringProperty()
    last_name = db.StringProperty()
    
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
        
    def isAdmin(self):
        """Check if user is admin"""
        return 'admin' in self.roles
     
    def __str__(self):
        """Print the user"""
        return '{'+self.nickname()+'}'
    
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

def local_login(nickname,passwd):
    """Log in user without google account.
    
    Args:
        nickname (str): Nickname to login with
        passwd (str): User local password
    
    Return (MyUser):
        Logged in user or None if failed.
    """
    user = get_user(nickname)
    if not user or user.password() != passwd:
        return None
    memcache.add('local_user',user)
    return user
    
def local_logout():
    """Log out user without google account."""
    memcache.delete('local_user')
    
def get_current_user():
    """Return the current user if someone logged in or None otherwise"""
    default_user = 'test@example.com'
    gUser = users.get_current_user()
    if not gUser:
        user = memcache.get('local_user')
        if not user:
            return None
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
        name = self.request.get('name')
        user = get_user(name)
        if user:
            user.delete()
        self.redirect('/')
        
class AddUser(webapp2.RequestHandler):
    def post(self):
        name = self.request.get('new-name')
        if len(name) > 0:
            create_user(name)
        self.redirect('/users')
        
