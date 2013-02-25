import unittest
from google.appengine.ext import testbed
from aclass import *

class TestClass(unittest.TestCase):
    
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
    
    def test_init(self):
        t = create_user('teacher1','teacher')
        c = create_class(t,'aaa')
        teacher = c.get_teacher()
        self.assertTrue( teacher != None )
        self.assertEqual( teacher.nickname() , 'teacher1' )
        
    def test_add_student(self):
        t = create_user('teacher1','teacher')
        c = create_class(t,'aaa')
        self.assertEqual(  c.name, 'aaa' )
        s1 = create_user('stu1','student')
        c.add_student(s1)
        self.assertEqual( len( c ), 1 )
        self.assertTrue( c.get_student(0) )
        self.assertTrue( c[0] )
        self.assertEqual(  c[0].nickname(), 'stu1' )
        s2 = create_user('stu2','student')
        c.add_student(s2)
        self.assertEqual( len( c ), 2 )
        self.assertEqual(  c[1].nickname(), 'stu2' )
        
    def test_get_teacher_classes(self):    
        t = create_user('teacher1','teacher')
        create_class(t,'aaa')
        create_class(t,'bbb')
        create_class(t,'ccc')
        
        classes = get_teacher_classes(t)
        self.assertEqual( len(classes), 3 )
        self.assertEqual( classes[0].name, 'aaa' )
        self.assertEqual( classes[1].name, 'bbb' )
        self.assertEqual( classes[2].name, 'ccc' )
        
    def test_get_student_classes(self):    
        t = create_user('teacher1','teacher')
        s1 = create_user('stu1','student')

        create_class(t,'aaa')
        bbb = create_class(t,'bbb')
        ccc = create_class(t,'ccc')
        
        bbb.add_student(s1)
        ccc.add_student(s1)
        
        classes = get_student_classes(s1)
        self.assertEqual( len(classes), 2 )
        self.assertTrue( s1.key() in bbb.students )
        self.assertTrue( s1.key() in ccc.students )
        