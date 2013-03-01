import webapp2
from google.appengine.ext import db
from myuser import MyUser,create_user,get_current_teacher
from mytemplate import write_template
from aclass import *

class TeacherStartPage(webapp2.RequestHandler):
    def get(self):
        teacher = get_current_teacher()
        if not teacher:
            self.redirect('/')
            
        template_values = {'classes': get_teacher_classes(teacher)}
        write_template(self, teacher, 'teacher_start.html', template_values)
        