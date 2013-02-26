import webapp2
import simplejson
from google.appengine.ext import db
from myuser import MyUser


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
            user.first_name = model['first_name']
            user.last_name = model['last_name']
            user.put()
        else:
            raise Exception('Saving of chapter failed')

    def post(self,Id=None):
        """Create new user instance and retirn its id which is its key"""
#        user = get_current_user()
#        if not user:
#            self.redirect('/')
            
        httpMethod = self.request.get('_method')
        if httpMethod == 'PUT':
            self.put(Id)
            return
        if httpMethod == 'DELETE':
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
        
        root = root_key()
        encoded_parent_key = model['parent_key']
        if encoded_parent_key == 'root':
            parent_key = root
        else:
            parent_key = db.Key(encoded=encoded_parent_key)
        
        title = model['title']
            
        if len(title) > 0:
            chapter = Chapter(parent=parent_key)
            chapter.authors.append(user.nickname())
            chapter.title = title
            chapter.put()
        else:
            self.response.out.write('error')
        
        self.response.out.write('{"id":"'+str(chapter.key())+'"}')

    def delete(self, Id):
        """Delete a chapter with key == Id"""
        chapter,ekey = get_chapter_by_encoded_key(Id)
        if chapter:
            chapter.deleteAll()
        else:
            raise Exception('Deleting of chapter failed')

