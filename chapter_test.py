import unittest
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import testbed
import chapter_module
from chapter_module import *

class TestChapter(unittest.TestCase):
    
    def createChapter(self,title,parent_key = None):
        if not parent_key:
            parent_key = root_key()
        chapter = Chapter(parent=parent_key)
        chapter.authors.append('user1')
        chapter.title = title
        chapter.put()
        return chapter.key()
        pass
        
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
    
    def tearDown(self):
        self.testbed.deactivate()
    
    def test_root_key(self):
        self.assertFalse(root_key() == None)
        self.assertEqual(str(root_key()), 'agx0ZXN0YmVkLXRlc3RyEQsSB0NoYXB0ZXIiBHJvb3QM')

    def test_get_chapter_by_encoded_key_root(self):
        chapter, ekey = get_chapter_by_encoded_key('root')
        self.assertTrue(isinstance(chapter,Chapter))
        self.assertEqual( ekey, str(root_key()) )

    def test_Chapter_create(self):
        parent_key = root_key()
        # create a top-level chapter
        chapter = Chapter(parent=parent_key)
        chapter.authors.append('user1')
        chapter.title = 'Chapter 1'
        chapter.put()
        key = chapter.key()
        
        # test that it is in datastore
        chapter1 = Chapter.get(key)
        self.assertNotEqual(chapter1,chapter)
        self.assertEqual(chapter1.title,'Chapter 1')
        self.assertEqual(chapter1.authors,['user1'])
        #print chapter1.parent_key
        
    def test_get_chapter_by_encoded_key(self):
        k1 = self.createChapter('Chap 1')
        k2 = self.createChapter('Chap 2')
        k3 = self.createChapter('Chap 3')
        chapter, ekey = get_chapter_by_encoded_key(str(k1))
        self.assertEqual(chapter.title,'Chap 1')
        chapter, ekey = get_chapter_by_encoded_key(str(k2))
        self.assertEqual(chapter.title,'Chap 2')
        chapter, ekey = get_chapter_by_encoded_key(str(k3))
        self.assertEqual(chapter.title,'Chap 3')
        