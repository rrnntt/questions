from google.appengine.api import memcache
from google.appengine.ext import testbed
import webapp2
import unittest
import webtest
import aclass_handlers
import teacher_handlers
from myuser import google_login,create_user
from aclass import Class,create_class,get_class_students

class HelloWorldHandler(webapp2.RequestHandler):
    def get(self):
        # Create the handler's response "Hello World!" in plain text.
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello World!')


class AppTest(unittest.TestCase):
    def setUp(self):
        # Create a WSGI application.
        app = webapp2.WSGIApplication([
                                       ('/', HelloWorldHandler),
                                       ('/students', aclass_handlers.Students),
                                       ('/teacherclass', teacher_handlers.ClassPage),
                                       ])
        self.testapp = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()
    
    def tearDown(self):
        self.testbed.deactivate()
    
    
    # Test the handler.
    def xtestHelloWorldHandler(self):
        response = self.testapp.get('/')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.normal_body, 'Hello World!')
        self.assertEqual(response.content_type, 'text/plain')
        
    def testStudentsAdd(self):
        teacher = create_user('te', 'teacher')
        google_login('te@gmail.com', 'te')
        clss = create_class(teacher,'class1')
        model = '{"nickname":"stu", "roles": "student", "clss": "'+str(clss.key())+'"}'
        params = {'_method': 'POST', 'model':model}
        response = self.testapp.post('/students',params)
        self.assertEqual(response.normal_body[0:7], '{"id":"')
        self.assertEqual(len(response.normal_body),51)
        
        clss = Class.get(clss.key())
        students = get_class_students(clss)
        self.assertEqual( len(students), 1)
        
    def testClassPage(self):
        teacher = create_user('te', 'teacher')
        google_login('te@gmail.com', 'te')
        clss = create_class(teacher,'class1')
        params = {'class': str(clss.key())}
        response = self.testapp.get('/teacherclass',params)
        self.assertTrue( len(response.normal_body) > 0 )
