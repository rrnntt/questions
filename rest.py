import webapp2
from google.appengine.ext import db
import simplejson
from myuser import get_current_user

class RESTHandlerClass(webapp2.RequestHandler):
    """REST service template class for managing a model.
    
    self.ModelClass = 
    
    """
    
    def put(self,Id):
        """Save a instance of a model with key == Id"""

#        obj = self.__class__.ModelClass.get(db.Key(encoded = Id))
        obj = self.ModelClass.get(db.Key(encoded = Id))

        if obj:
            json = simplejson.decoder.JSONDecoder()
            model = json.decode( self.request.get('model'))
            
            for field in model:
                if not field in model:
                    self.response.out.write('error: required field not found.')
                    return
                else:
                    setattr(obj, field, model[field])
            
            obj.put()
        else:
            raise Exception('Saving of model failed')

    def post(self,Id=None):
        """Create new chapter instance and retirn its id which is its key"""
        user = get_current_user()
        if not user:
            self.redirect('/')
            return
        
        #raise Exception(self.request.get('_method'))
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
            
        # retrieve and decode the model from the client side
        json = simplejson.decoder.JSONDecoder()
        model = json.decode( self.request.get('model'))

        # create instance of ModelClass (if asked with a parent)
        if 'parent' in model:
            parent_key = db.Key(encoded=model['parent'])
#            obj = self.__class__.ModelClass( parent = parent_key )
            obj = self.ModelClass( parent = parent_key )
        else:
#            obj = self.__class__.ModelClass()
            obj = self.ModelClass()
            
        # set all required fields in model
#        for field in self.__class__.required:
        for field in self.required:
            if not field in model:
                self.response.out.write('error: required field not found.')
                return
            else:
                setattr(obj, field, model[field])
                # mark field as used
                model[field] = None
                
        # set optional fields
        for field in model:
            value = model[field]
            if value != None:
                setattr(obj, field, value)
                
        obj.put()
        
        self.response.out.write('{"id":"'+str(obj.key())+'"}')

    def delete(self, Id):
        """Delete a chapter with key == Id"""
#        question = self.__class__.ModelClass.get(db.Key(encoded = Id))
        question = self.ModelClass.get(db.Key(encoded = Id))
        if question:
            question.delete()
        else:
            raise Exception('Deleting of question failed')


