import webapp2
from google.appengine.ext import db
from base_handler import BaseHandler
from myuser import MyUser,create_user
from mytemplate import write_template
from aclass import *
from question_list import QuestionList, get_question_list
from course import Course, get_courses

class StartPage(BaseHandler):
    def get(self):
        teacher = self.get_current_teacher()
        if not teacher:
            self.redirect('/')
            return
            
        template_values = {'classes': get_teacher_classes(teacher)}
        write_template(self, teacher, 'teacher_start.html', template_values)
        
class ClassPage(BaseHandler):
    def get(self):
        teacher = self.get_current_teacher()
        if not teacher:
            self.redirect('/')
            return
            
        class_key = db.Key(encoded=self.request.get('class'))
        clss = Class.get(class_key)
        students = get_class_students(clss)
        courses = get_courses(clss)
        
        # add course progress to each student
        for stu in students:
            prog = []
            for c in courses:
                s = '{:.2%}'.format(c.get_progress(stu))
                prog.append( s )
            stu.progress = prog 
        
        #raise Exception('stu:'+str(len(clss)))
        template_values = {'students': students,
                           'clss': clss,
                           'qlists': get_question_list(clss),
                           'courses': courses
                           }
        write_template(self, teacher, 'teacher_class.html', template_values)
                