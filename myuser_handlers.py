import webapp2
import json
from google.appengine.ext import db
from google.appengine.api import users

from base_handler import BaseHandler
from myuser import MyUser, create_user
#from aclass import Class
from mytemplate import write_template

####################################################################
#   MyUser REST service
####################################################################
class MyUsers(BaseHandler):
    """Implements REST service for managing users"""
    def put(self,Id):
        """Save a user with key == Id"""
        user = MyUser.get( db.Key(encoded=Id) )
        #chapter,ekey = get_chapter_by_encoded_key(Id)
        if user:
            jsn = json.decoder.JSONDecoder()
            model = jsn.decode( self.request.get('model'))
            user.from_json(model)
            user.put()
        else:
            raise Exception('Saving of user failed')

    def post(self,Id=None):
        """Create new user instance and return its id which is its key"""
        admin = self.get_current_admin()
        if not admin:
            self.redirect('/')
            return
            
        httpMethod = self.request.get('_method')
        if httpMethod == 'PUT':
            self.put(Id)
            return
        if httpMethod == 'DELETE':
            #raise Exception("deleting...")
            self.delete(Id)
            return
        if httpMethod == 'GET':
            raise Exception('GET not implemented')
            return
            
        jsn = json.decoder.JSONDecoder()
        model = jsn.decode( self.request.get('model'))
        #raise Exception(model[0])
        if not 'nickname' in model:
            self.response.out.write('error')
        
        nickname = model['nickname']
        if 'password' in model:
            password = model['password']
        else:
            password = None
        roles = model['roles']
        
        if roles == 'student' and not 'clss' in model: 
            self.response.out.write('error: no clss keyword')
            return
            
        if len(nickname) > 0:
            try:
                new_user = create_user(nickname, roles, password)
            except:
                self.response.out.write('User cannot be created (exists already?)')
                return
            if not new_user:
                self.response.out.write('error')
                return
            new_user.from_json(model)
            new_user.put()

        else:
            self.response.out.write('error')
        
        #raise Exception('OK: '+str(new_user.key()))
        self.response.out.write('{"id":"'+str(new_user.key())+'"}')

    def delete(self, Id):
        """Delete a user with key == Id"""
        user = MyUser.get( db.Key(encoded=Id) )
        if user:
            user.delete()

#########################################################################
#    Request handlers
#########################################################################

class UserList(BaseHandler):
    def get(self):

        user = self.get_current_admin()
        if not user:
            self.redirect('/')
            return
        
        query = MyUser.all()
        user_list = []
        for u in query.run():
            if len(u.roles) > 1 or 'student' not in u.roles:
                user_list.append(u)        
            
        template_values = {
            'user_list': user_list,
        }
        write_template(self, user, 'user_list.html',template_values)
        
class EditUserPage(BaseHandler):
    def get(self):

        user = self.get_current_admin()
        if not user:
            self.redirect('/')
            return
        
        key = self.request.get('user')
        euser = db.get(key)
        roles = []
        for role in euser.roles:
            roles.append(str(role))
        
        template_values = {
            'euser': euser,
            'euser_roles': roles,
        }
        write_template(self, user, 'user_edit.html',template_values)
        
##################################################################################
        
class DeleteUser(BaseHandler):
    def post(self):
        encoded_key = self.request.get('key')
        key = db.Key(encoded=encoded_key)
        user = MyUser.get(key)
        if user:
            user.delete()
        self.redirect('/userlist')
        
class AddUser(BaseHandler):
    def post(self):
        name = self.request.get('new-name')
        if len(name) > 0:
            create_user(name)
        self.redirect('/userlist')
        
