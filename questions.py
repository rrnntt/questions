#import cgi
#import datetime
import urllib
import webapp2

from google.appengine.ext import db
from google.appengine.api import users

import jinja2
import os
from computerjanitor import exc

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MyUser(db.Model):
    user = db.UserProperty()
    roles = db.StringListProperty()
    _nickname = db.StringProperty()
    def nickname(self):
        if self.user:
            return self.user.nickname()
        else:
            return self._nickname
    def isAdmin(self):
        return 'admin' in self.roles 
    def __str__(self):
        return '{'+self.nickname()+'}'
    
def get_user(name):
    user = MyUser.get_by_key_name(name)
    return user

def create_user(name,roles=None):
    user = get_user(name)
    if not user:
        user = MyUser(key_name=name)
        user._nickname = name
        if roles:
            if isinstance(roles, list):
                user.roles = roles
            else:
                user.roles.append(roles)
        user.put()
    else:
        #raise Exception('User '+name+' exists')
        user._nickname = name
    return user

def get_current_user():
    default_user = 'test@example.com'
    gUser = users.get_current_user()
    if not gUser or gUser.nickname() != default_user:
        return None
    user = get_user(gUser.nickname())
    if user and not user.user:
        user.user = gUser 
    if not user and gUser.nickname() == default_user:
        user = MyUser(key_name=default_user)
        user.user = gUser
        user.roles.append('admin')
        #user.put()
    #user.roles = []
    return user

class MainPage(webapp2.RequestHandler):
    def get(self):

        user = get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            user_name = user.nickname()
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            user_name = ''
        
        guser = users.get_current_user()
        if guser:
            guser_name = guser.nickname()
        else:
            guser_name = ''

        template_values = {
            'user': user,
            'user_name': user_name,
            'login_url': url,
            'login_url_text': url_linktext,
            'guser_name': guser_name,
        }

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

class UserList(webapp2.RequestHandler):
    def get(self):

        user_list = MyUser.all().fetch(1000)
            
        template_values = {
            'user_list': user_list,
        }
        template = jinja_environment.get_template('user_list.html')
        self.response.out.write(template.render(template_values))
        
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
        

app = webapp2.WSGIApplication([(r'/', MainPage),
                               (r'/users', UserList),
                               (r'/deleteuser', DeleteUser),
                               (r'/adduser', AddUser),
                               ],
                              debug=True)
