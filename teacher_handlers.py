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
            
        template_values = {'classes': get_teacher_classes(teacher)}
        write_template(self, teacher, 'teacher_start.html', template_values)
        
class ClassPage(webapp2.RequestHandler):
    def get(self):
        teacher = get_current_teacher()
        if not teacher:
            self.redirect('/')
            
        class_key = db.Key(encoded=self.request.get('class'))
        aclass = Class.get(class_key)
        template_values = {'students': get_class_students(aclass)}
        write_template(self, teacher, 'teacher_class.html', template_values)
                