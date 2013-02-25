import unittest
from google.appengine.ext import testbed
from question import *

class TestQuestion(unittest.TestCase):
    
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
    
    def test_new_question(self):
        q = Question( text = 'What?', answer = 'No')
        q.put()
        
        qq = Question.get(q.key())
        self.assertEqual( qq.text, 'What?' ) 
        self.assertEqual( qq.answer, 'No' )
        self.assertEqual( qq.class_name(), 'Question' )
        
    def test_new_composite_question(self):
        q = CompositeQuestion( text = 'What?', answer = 'No')
        q.put()
        
        qq = Question.get(q.key())
        self.assertEqual( qq.text, 'What?' ) 
        self.assertEqual( qq.answer, 'No' )
        self.assertEqual( qq.class_name(), 'CompositeQuestion' )
        self.assertTrue( hasattr(qq, 'add_question') )
        self.assertTrue( isinstance( qq, CompositeQuestion ) )
            
    def test_add_question(self):
        q = CompositeQuestion()
        q1 = Question(text='What?',answer='Yes')
        q1.put()
        q2 = Question(text='When?',answer='Stop')
        q2.put()
        q.add_question(q1)
        q.add_question(q2)
        q.put()
        
        qq = Question.get(q.key())
        self.assertEqual( qq.text, None ) 
        self.assertEqual( qq.answer, None )
        self.assertEqual( qq.class_name(), 'CompositeQuestion' )
        self.assertTrue( isinstance( qq, CompositeQuestion ) )
        self.assertEqual( len(qq), 2 ) 
        
        qq1 = qq[0]
        self.assertEqual( qq1.text, 'What?' ) 
        self.assertEqual( qq1.answer, 'Yes' )
        self.assertEqual( qq1.class_name(), 'Question' )
        
        qq2 = qq[1]
        self.assertEqual( qq2.text, 'When?' ) 
        self.assertEqual( qq2.answer, 'Stop' )
        self.assertEqual( qq2.class_name(), 'Question' )
        
        ans = qq.get_answer()
        self.assertEqual( ans, ['Yes', 'Stop'] )
        self.assertEqual( qq1.get_answer(), 'Yes' )
        self.assertEqual( qq2.get_answer(), 'Stop' )
                        