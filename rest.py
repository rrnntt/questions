import webapp2
from google.appengine.ext import db
import simplejson
from google.appengine.api import memcache
from myuser import get_current_user

class RESTHandlerClass(webapp2.RequestHandler):
    """REST service template class for managing a model.
    
    self.ModelClass = 
    
    """
    def __init__(self, request=None, response=None):
        webapp2.RequestHandler.__init__(self, request, response)
        self.obj = None
        
    def convert(self,field,value):
        """
        Convert value for a model fieeld from str to actual type.
        Method must be overriden if there are non-string fields.
        
        By default returns input value without convertion
        """
        return value

    def get(self,Id):
        """Save a instance of a model with key == Id"""
        self.obj = self.ModelClass.get(db.Key(encoded = Id))
        if self.obj:
            attrs = self.ModelClass.__dict__
            out = '{'
            for attr in attrs:
                prop = attrs[attr]
                if isinstance(prop,db.Property):
                    out += '"' + attr + '":"' + str(getattr(self.obj,attr)) + '",'
            out += '}'
            raise Exception(out) 
            self.response.out.write('{"name":"hello1"}')
        else:
            raise Exception('Object not found '+Id)
    
    def put(self,Id):
        """Save a instance of a model with key == Id"""

#        obj = self.__class__.ModelClass.get(db.Key(encoded = Id))
        self.obj = self.ModelClass.get(db.Key(encoded = Id))

        if self.obj:
            json = simplejson.decoder.JSONDecoder()
            model = json.decode( self.request.get('model'))
            
            for field in model:
                if not field in model:
                    self.response.out.write('error: required field not found.')
                    return
                else:
                    setattr(self.obj, field, self.convert(field, model[field]))
            
            self.obj.put()
        else:
            raise Exception('Saving of model failed '+Id)

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
            self.obj = self.ModelClass( parent = parent_key )
        else:
#            obj = self.__class__.ModelClass()
            self.obj = self.ModelClass()
            
        # set all required fields in model
#        for field in self.__class__.required:
        for field in self.required:
            if not field in model:
                self.response.out.write('error: required field not found.')
                return
            else:
                setattr(self.obj, field, self.convert(field, model[field]))
                # mark field as used
                model[field] = None
                
        # set optional fields
        for field in model:
            value = model[field]
            if value != None:
                #setattr(self.obj, field, value)
                setattr(self.obj, field, self.convert(field, value))
                
        self.obj.put()
        
        self.response.out.write('{"id":"'+str(self.obj.key())+'"}')

    def delete(self, Id):
        """Delete a chapter with key == Id"""
#        question = self.__class__.ModelClass.get(db.Key(encoded = Id))
        obj = self.ModelClass.get(db.Key(encoded = Id))
        if obj:
            obj.delete()
        else:
            raise Exception('Deleting of object failed')


class MemcachedRESTHandler(RESTHandlerClass):
    def __init__(self, request=None, response=None):
        RESTHandlerClass.__init__(self, request, response)
        # implementation must define string self.cache_key
        self.cache_key = None
        
    def post(self,Id=None):
        out = RESTHandlerClass.post(self, Id)
        
        if Id == None:
            qlist = memcache.get(self.cache_key)
            if qlist != None:
                qlist.delete()
            memcache.delete(self.cache_key)
            if self.obj != None:
                memcache.add(self.cache_key,self.obj)
            
        return out            

    def put(self,Id):
        RESTHandlerClass.put(self, Id)
        qlist = memcache.get(self.cache_key)
        if qlist.key() == self.obj.key():
            qlist = self.obj

    def delete(self,Id):
        qlist = memcache.get(self.cache_key)
        if qlist != None:
            key = db.Key(encoded = Id)
            if key == qlist.key():
                memcache.delete(self.cache_key)
        RESTHandlerClass.put(self, Id)
        
