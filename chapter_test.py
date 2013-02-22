import unittest
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import testbed
import chapter_module
from chapter_module import *
from myuser import *

class TestChapter(unittest.TestCase):
    
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

    def test_create_chapter(self):
        author = create_user('user1', 'teacher')
        # create a top-level chapter
        chapter = create_chapter(root_key(),author,'Chapter 1')
        key = chapter.key()
        
        # test that it is in datastore
        chapter1 = Chapter.get(key)
        self.assertNotEqual(chapter1,chapter)
        self.assertEqual(chapter1.title,'Chapter 1')
        self.assertEqual(chapter1.authors[0], author.key())
        self.assertEqual(chapter1.get_author().key(), author.key())
        #print chapter1.parent_key
        
    def test_get_chapter_by_encoded_key(self):
        author = create_user('name', 'teacher')
        k1 = create_chapter(root_key(),author,'Chap 1')
        k2 = create_chapter(root_key(),author,'Chap 2')
        k3 = create_chapter(root_key(),author,'Chap 3')
        chapter, ekey = get_chapter_by_encoded_key(str(k1.key()))
        self.assertEqual(chapter.title,'Chap 1')
        chapter, ekey = get_chapter_by_encoded_key(str(k2.key()))
        self.assertEqual(chapter.title,'Chap 2')
        chapter, ekey = get_chapter_by_encoded_key(str(k3.key()))
        self.assertEqual(chapter.title,'Chap 3')

    def test_add_author(self):
        author1 = create_user('user1', 'teacher')
        author2 = create_user('user2', 'teacher')
        author3 = create_user('user3', 'teacher')
        # create a top-level chapter
        chapter = create_chapter(root_key(),author1,'Chapter 1')
        self.assertTrue( chapter.canEdit(author1) )
        self.assertFalse( chapter.canEdit(author2) )
        self.assertFalse( chapter.canEdit(author3) )
        chapter.add_author(author2)
        self.assertTrue( chapter.canEdit(author1) )
        self.assertTrue( chapter.canEdit(author2) )
        self.assertFalse( chapter.canEdit(author3) )
        chapter.add_author(author3)
        self.assertTrue( chapter.canEdit(author1) )
        self.assertTrue( chapter.canEdit(author2) )
        self.assertTrue( chapter.canEdit(author3) )
        self.assertEqual(chapter.get_author_count(),3)
        chapter.remove_author(author2)
        self.assertTrue( chapter.canEdit(author1) )
        self.assertFalse( chapter.canEdit(author2) )
        self.assertTrue( chapter.canEdit(author3) )
        self.assertEqual(chapter.get_author_count(),2)
        chapter.remove_author(author3)
        self.assertTrue( chapter.canEdit(author1) )
        self.assertFalse( chapter.canEdit(author2) )
        self.assertFalse( chapter.canEdit(author3) )
        self.assertEqual(chapter.get_author_count(),1)
        chapter.remove_author(author1)
        self.assertEqual(chapter.get_author_count(),1)
        
        
        