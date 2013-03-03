import unittest
import os
from google.appengine.ext import testbed
from myuser import *

class TestMyUser(unittest.TestCase):
    
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
    
    def test_create(self):
        create_user('user1','student')
        test_user = get_user('user1')
        self.assertEqual(test_user.nickname(), 'user1')
        
    def test_user_with_gmail_domain(self):
        # create user with nickname 'tst'
        create_user('tst','student')
        # log in
        google_login('tst@gmail.com','bob')
        user = get_current_user()
        self.assertTrue(user != None)
        self.assertEqual( user.nickname(), 'tst' )
        self.assertEqual( user.email(), 'tst@gmail.com' )
        self.assertEqual( user.roles, ['student'] )
        user.set_email('bob@example.com')
        user = get_current_user()
        self.assertEqual( user.email(), 'bob@example.com' )

    def test_user_with_different_domain(self):
        # user from different domain
        create_user('tst@example.com','student')
        google_login('tst@example.com','bob')
        user = get_current_user()
        self.assertTrue(user != None)
        self.assertEqual( user.nickname(), 'tst@example.com' )
        self.assertEqual( user.email(), 'tst@example.com' )
        self.assertEqual( user.roles, ['student'] )
        user.set_email('bob@example.com')
        user = get_current_user()
        self.assertEqual( user.email(), 'bob@example.com' )
                
    def test_local_login(self):
        create_user('user1','student','123')
        local_login('user1','123')
        user = get_current_user()
        self.assertTrue(user != None)
        self.assertEqual( user.nickname(), 'user1' )
        self.assertEqual( user.roles, ['student'] )
        self.assertEqual( user.email(), None )
        user.set_email('user1@example.com')
        user = get_current_user()
        self.assertEqual( user.email(), 'user1@example.com' )
        
    def test_wrong_local_login(self):
        create_user('user1','student','123')
        self.assertFalse( local_login('user1','321') )
        user = get_current_user()
        self.assertTrue(user == None)
        self.assertFalse( local_login('user2','123') )
        user = get_current_user()
        self.assertTrue(user == None)
        
    def test_local_logout(self):
        create_user('user1','student','123')
        local_login('user1','123')
        user = get_current_user()
        self.assertTrue(user != None)
        self.assertEqual( user.nickname(), 'user1' )
        self.assertEqual( user.roles, ['student'] )
        local_logout()
        user = get_current_user()
        self.assertTrue(user == None)
        # log out second time to see that it is safe to log out any number of times
        local_logout()
        user = get_current_user()
        self.assertTrue(user == None)
        
        