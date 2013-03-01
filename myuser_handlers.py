import webapp2
import simplejson
from google.appengine.ext import db
from myuser import MyUser,create_user,get_current_admin
from aclass import Class

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
            json = simplejson.decoder.JSONDecoder()
            model = json.decode( self.request.get('model'))
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
            
        json = simplejson.decoder.JSONDecoder()
        model = json.decode( self.request.get('model'))
        #raise Exception(model[0])
        if not 'nickname' in model:
            self.response.out.write('error')
        
        nickname = model['nickname']
        password = model['password']
        email = model['email']
        roles = model['roles']
            
        if len(nickname) > 0:
            new_user = create_user(nickname, roles, password)
            if not new_user:
                self.response.out.write('error')
                return
            if len(email) > 0:
                new_user.set_email(email)
            if new_user.isStudent():
                clss_encoded_key = model['clss']
                if len(clss_encoded_key) > 0:
                    clss = Class.get( db.Key(encoded=clss_encoded_key) )
                    if clss:
                        clss.add_student(new_user)
        else:
            self.response.out.write('error')
        
        self.response.out.write('{"id":"'+str(new_user.key())+'"}')

    def delete(self, Id):
        """Delete a user with key == Id"""
        user = MyUser.get( db.Key(encoded=Id) )
        if user:
            user.delete()

