import webapp2
from google.appengine.ext import db
from myuser import MyUser,create_user,get_current_teacher
from mytemplate import write_template
from aclass import *

class StartPage(webapp2.RequestHandler):
    def get(self):
        teacher = get_current_teacher()
        if not teacher:
            self.redirect('/')
            return
            
        template_values = {'classes': get_teacher_classes(teacher)}
        write_template(self, teacher, 'teacher_start.html', template_values)
        
class ClassPage(webapp2.RequestHandler):
    def get(self):
        teacher = get_current_teacher()
        if not teacher:
            self.redirect('/')
            return
            
        class_key = db.Key(encoded=self.request.get('class'))
        clss = Class.get(class_key)
        students = get_class_students(clss)
        #raise Exception('stu:'+str(len(clss)))
        template_values = {'students': students,
                           'clss': clss,
                           }
        write_template(self, teacher, 'teacher_class.html', template_values)
                