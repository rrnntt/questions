import webapp2
import simplejson
from google.appengine.ext import db
from aclass import Class, create_class
from myuser import get_current_teacher

####################################################################
#   Class REST service
####################################################################
class Classes(webapp2.RequestHandler):
    """Implements REST service for managing classes"""
    def put(self,Id):
        """Save a user with key == Id"""
        clss = Class.get( db.Key(encoded=Id) )
        if clss:
            json = simplejson.decoder.JSONDecoder()
            model = json.decode( self.request.get('model'))
            clss.name = model['name']
            clss.put()
        else:
            raise Exception('Saving of class failed')

    def post(self,Id=None):
        """Create new class instance and retirn its id which is its key"""
        teacher = get_current_teacher()
        if not teacher:
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
        if not 'name' in model:
            self.response.out.write('error')
        
        name = model['name']
            
        if len(name) > 0:
            new_clss = create_class(teacher, name)
            if new_clss == None:
                self.response.out.write('error')
                return
        else:
            self.response.out.write('error')
        
        self.response.out.write('{"id":"'+str(new_clss.key())+'"}')

    def delete(self, Id):
        """Delete a user with key == Id"""
        user = Class.get( db.Key(encoded=Id) )
        if user:
            user.delete()

