import webapp2
import json
from google.appengine.ext import db
from myuser import MyUser,create_user,get_current_admin
from aclass import Class
from mytemplate import write_template

####################################################################
#   MyUser REST service
####################################################################
class MyUsers(webapp2.RequestHandler):
    """Implements REST service for managing users"""
    def put(self,Id):
        """Save a user with key == Id"""
        user = MyUser.get( db.Key(encoded=Id) )
        #chapter,ekey = get_chapter_by_encoded_key(Id)
        if user:
            jsn = json.decoder.JSONDecoder()
            model = jsn.decode( self.request.get('model'))
            user._first_name = model['first_name']
            user._last_name = model['last_name']
            user.put()
        else:
            raise Exception('Saving of user failed')

    def post(self,Id=None):
        """Create new user instance and retirn its id which is its key"""
        admin = get_current_admin()
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
        password = model['password']
#        email = model['email']
        roles = model['roles']
        
        if roles == 'student' and not 'clss' in model: 
            self.response.out.write('error: no clss keyword')
            return
            
        if len(nickname) > 0:
            new_user = create_user(nickname, roles, password)
            if not new_user:
                self.response.out.write('error')
                return
            new_user.from_json(model)

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

class UserList(webapp2.RequestHandler):
    def get(self):

        user = get_current_admin()
        if not user:
            self.redirect('/')
            return
        
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
        
