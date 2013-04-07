from google.appengine.api import memcache
from google.appengine.ext import testbed
import webapp2
import unittest
import webtest
from rest import *
from myuser import create_user, google_login


class TestModel(db.Model):
    text = db.StringProperty()
    
#class TestRESTMeta(type):
#    def __init__(cls, name, bases, namespace):
#        super(TestRESTMeta, cls).__init__(name, bases, namespace)
#        cls.ModelClass = TestModel
#        cls.required = ['text']
    
class TestRESTHandler(RESTHandlerClass):
    #__metaclass__ = TestRESTMeta
    def __init__(self, request=None, response=None):
        RESTHandlerClass.__init__(self, request, response)
        self.ModelClass = TestModel
        self.required = ['text']

class RESTTest(unittest.TestCase):
    
    def setUp(self):
        # Create a WSGI application.
        app = webapp2.WSGIApplication([
                                       (r'/test', TestRESTHandler),
                                       (r'/test/(.+)', TestRESTHandler),
                                       ])
        self.testapp = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()
    
    def tearDown(self):
        self.testbed.deactivate()
    
    def testRESTHandlerPOST(self):
        """
        Test REST POST command which creates a new instance of a model
        and saves it in the database. URL = '/test'
        """
        # we need to have a user
        teacher = create_user('te', 'teacher')
        # which must be logged in
        google_login('te@gmail.com', 'te')
        # model is what backbone.js sends when its save() mathod is called
        model = '{"text":"Hello world!"}'
        # these are http parameters sent by backbone
        params = {'_method': 'POST', 'model':model}
        # emulate sending POST by web browser and receiving it by the REST handler
        response = self.testapp.post('/test',params)
        # REST handler must return key of the created instance as "id" field
        # in the json object
        self.assertEqual(response.normal_body[0:7], '{"id":"')
        self.assertEqual(len(response.normal_body),51)
        encoded_key = response.normal_body[7:-2]
        key = db.Key(encoded=encoded_key)
        inst = TestModel.get(key)
        self.assertTrue( inst != None )
        self.assertEqual( inst.text, 'Hello world!' )
        
    def testRESTHandlerGET(self):
        """
        Test REST GET command which returns an instance of a model
        which is already in the database. URL = '/test/key_string'
        """
        # we need to have a user
        create_user('te', 'teacher')
        # which must be logged in
        google_login('te@gmail.com', 'te')
        # add an instance to the database
        inst = TestModel()
        inst.text = 'saved model'
        inst.put()
        #  TODO: I don't know what parameters backbone sends with GET or what 
        #  response it expects

    def testRESTHandlerPUT(self):
        """
        Test REST PUT command which mofifies an instance of a model
        which is already in the database. URL = '/test/key_string'
        """
        # we need to have a user
        create_user('te', 'teacher')
        # which must be logged in
        google_login('te@gmail.com', 'te')
        # add an instance to the database
        inst = TestModel()
        inst.text = 'saved model'
        inst.put()
        # these are http parameters sent by backbone
        params = {'_method': 'PUT', 'model':'{"text":"Barnacles!"}'}
        # emulate sending POST by web browser and receiving it by the REST handler
        response = self.testapp.post('/test/'+str(inst.key()),params)
        inst = TestModel.get(inst.key())
        self.assertEqual( inst.text, 'Barnacles!' )
        self.assertEqual( response.normal_body, '' )

    def testRESTHandlerDELETE(self):
        """
        Test REST DELETE command which deletes an instance of a model
        which is already in the database. URL = '/test/key_string'
        """
        # we need to have a user
        create_user('te', 'teacher')
        # which must be logged in
        google_login('te@gmail.com', 'te')
        # add an instance to the database
        inst = TestModel()
        inst.text = 'saved model'
        inst.put()
        self.assertEqual( len(TestModel.all().fetch(100)), 1 )
        # these are http parameters sent by backbone
        params = {'_method': 'DELETE', 'model':'{"text":"Barnacles!"}'}
        # emulate sending DELETE by web browser and receiving it by the REST handler
        response = self.testapp.post('/test/'+str(inst.key()),params)
        self.assertEqual( len(TestModel.all().fetch(100)), 0 )
