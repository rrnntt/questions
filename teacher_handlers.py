import json
from base_handler import BaseHandler

from mytemplate import write_template
from aclass import *
from question_list import get_question_list
from course import get_courses
from mymarkdown import markdown_questionlists
from student_results import get_student_result

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

class EditClassPage(BaseHandler):
    def get(self):
        teacher = self.get_current_teacher()
        if not teacher:
            self.redirect('/')
            return
            
        class_key = db.Key(encoded=self.request.get('class'))
        clss = Class.get(class_key)
        students = get_class_students(clss)
        
        template_values = {'students': students,
                           'clss': clss,
                           }
        write_template(self, teacher, 'teacher_class_edit.html', template_values)
                
class StudentPage(BaseHandler):
    def get(self):
        teacher = self.get_current_teacher()
        if not teacher:
            self.redirect('/')
            return
        clss = db.get( self.request.get('class') )
        student = db.get( self.request.get('student') )
        qlists = get_question_list(clss)
        markdown_questionlists(qlists)
        courses = get_courses(clss)
        for course in courses:
            course.qlists = course.get_chapters()
            markdown_questionlists(course.qlists)
            for qlist in course.qlists:
                for q in qlist.questions:
                    q.result = get_student_result(student, q)                    
        
        template_values = {
                           'student': student,
                           'clss': clss,
                           'qlists': qlists,
                           'courses': courses,
                           }
        write_template(self, teacher, 'teacher_student.html', template_values)
        
class MarkResult(BaseHandler):
    def get(self):
        user = self.get_current_teacher()
        if not user:
            self.redirect('/')
            return
        
        try:
            result = db.get( self.request.get('result') )
        except:
            self.redirect('/')
            return
            
        mark = self.request.get('mark')
        result.result = mark
        result.put()

        res = {}
        res['status'] = 'OK'

        self.response.out.write(json.dumps(res))

