from google.appengine.api import memcache
from google.appengine.ext import testbed
import webapp2
import unittest
import webtest
from myuser import MyUser,google_login,create_user
from chapter_module import Chapters


class ChapterTest(unittest.TestCase):
    def setUp(self):
        # Create a WSGI application.
        app = webapp2.WSGIApplication([
                                       (r'/chapters', Chapters),
                                       (r'/chapters/(.+)', Chapters),
                                       ])
        self.testapp = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()
    
    def tearDown(self):
        self.testbed.deactivate()
    
    def testAddChapter(self):
        teacher = create_user('te', 'teacher')
        google_login('te@gmail.com', 'te')
        model = '{"title":"Chapter 1", "parent_key": "root"}'
        params = {'_method': 'POST', 'model':model}
        response = self.testapp.post('/chapters',params)
        self.assertEqual(response.normal_body[0:7], '{"id":"')
        self.assertEqual(len(response.normal_body),71)
