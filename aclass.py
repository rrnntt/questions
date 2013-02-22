import webapp2
from google.appengine.ext import db
#from google.appengine.api import memcache
import myuser
from myuser import *

class Class(db.Model):
    name = db.StringProperty()
    student_keys = db.ListProperty(db.Key)
    
    def get_teacher(self):
        teacher = MyUser.get(self.parent_key())
        if not teacher:
            raise Exception('Class teacher not found')
        if not 'teacher' in teacher.roles:
            raise Exception('Class without teacher')
        return teacher
        
    def add_student(self, student):
        self.student_keys.append( student.key() )
        
    def get_student(self,i):
        k = self.student_keys[i]
        return MyUser.get(k)

    def __getitem__(self, i):
        return self.get_student(i)
    
    def __len__(self):
        return len(self.student_keys)
    
def create_class(teacher, name):
    c = Class(parent = teacher)
    c.name = name
    c.put()
    return c
    
    
def get_classes(teacher):
    query = Class.all().ancestor(teacher.key())
    return query.fetch(1000)
    