import webapp2
import json
from google.appengine.ext import db
from aclass import Class, create_class, get_student_classes
from myuser import get_current_teacher,get_current_student,MyUser,create_user

####################################################################
#   Class REST service
####################################################################
class Classes(webapp2.RequestHandler):
    """Implements REST service for managing classes"""
    def put(self,Id):
        """Save a class with key == Id"""
        clss = Class.get( db.Key(encoded=Id) )
        if clss:
            jsn = json.decoder.JSONDecoder()
            model = jsn.decode( self.request.get('model'))
            clss.name = model['name']
            clss.put()
        else:
            raise Exception('Saving of class failed')

    def post(self,Id=None):
        """Create new class instance and retirn its id which is its key"""
        teacher = get_current_teacher()
        if not teacher:
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
            return
        
        self.response.out.write('{"id":"'+str(new_clss.key())+'"}')

    def delete(self, Id):
        """Delete a user with key == Id"""
        user = Class.get( db.Key(encoded=Id) )
        if user:
            user.delete()

####################################################################
#   Student REST service
####################################################################
class Students(webapp2.RequestHandler):
    """Implements REST service for managing students"""
    def put(self,Id):
        """Save a student with key == Id"""
        student = MyUser.get( db.Key(encoded=Id) )
        if student:
            jsn = json.decoder.JSONDecoder()
            model = jsn.decode( self.request.get('model'))
            student.from_json( model )
            student.put()
        else:
            raise Exception('Saving of student failed')

    def post(self,Id=None):
        """Create new class instance and retirn its id which is its key"""
        teacher = get_current_teacher()
        if not teacher:
            self.redirect('/')
            return
        
        #raise Exception('uri='+self.request.uri)
            
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
        #raise Exception('model '+self.request.get('model'))
        model = jsn.decode( self.request.get('model'))
        
        if not 'clss' in model:
            raise Exception('Class is missing from model.')
            
        try:
            student = create_user(model)
        except:
            self.response.out.write('error')
            return
        
        clss_encoded_key = model['clss']
        clss = Class.get( db.Key(encoded=clss_encoded_key) )
        if clss != None:
            #try:
            clss.add_student(student)
            #except:
            #    raise Exception('failed to add student')
        else:
            raise Exception('Class not found.')

        #raise Exception('stu key: '+str(self.request.uri) + ' ' + str(model))
        self.response.out.write('{"id":"'+str(student.key())+'"}')

    def delete(self, Id):
        """Delete a student with key == Id"""
        student = MyUser.get( db.Key(encoded=Id) )
        if student != None:
            classes = get_student_classes(student)
            for c in classes:
                c.remove_student(student)
            if student.isLocal():
                student.delete()

