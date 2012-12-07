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
    if not gUser:
        return None
    #raise Exception(str(gUser))
    user = get_user(gUser.nickname())
    if user and not user.user:
        user.user = gUser 
    if not user and gUser.nickname() == default_user:
        user = MyUser(key_name=default_user)
        user.user = gUser
        user.roles.append('admin')
        user.put()
    # temporary:
    if gUser.nickname() == default_user:
        user.roles = ['admin']
    return user

def get_current_admin():
    user = get_current_user()
    if not user or not user.isAdmin():
        return None
    return user

def write_template(handler, user, file_name, template_values = {}):
        if user:
            url = users.create_logout_url(handler.request.uri)
            url_linktext = 'Logout'
            user_name = user.nickname()
        else:
            url = users.create_login_url(handler.request.uri)
            url_linktext = 'Login'
            user_name = ''
        template_values['user'] = user
        template_values['user_name'] = user_name
        template_values['login_url'] = url
        template_values['login_url_text'] = url_linktext
        template = jinja_environment.get_template(file_name)
        handler.response.out.write(template.render(template_values))

class MainPage(webapp2.RequestHandler):
    def get(self):

        user = get_current_user()
        
        #template = jinja_environment.get_template('index.html')
        #self.response.out.write(template.render(template_values))
        write_template(self, user, 'index.html')

class UserList(webapp2.RequestHandler):
    def get(self):

        user = get_current_admin()
        if not user:
            self.redirect('/')
        
        user_list = MyUser.all().fetch(1000)
            
        template_values = {
            'user_list': user_list,
        }
        #template = jinja_environment.get_template('user_list.html')
        #self.response.out.write(template.render(template_values))
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
        

app = webapp2.WSGIApplication([(r'/', MainPage),
                               (r'/users', UserList),
                               (r'/deleteuser', DeleteUser),
                               (r'/adduser', AddUser),
                               ],
                              debug=True)
