from base_handler import BaseHandler
from google.appengine.api import memcache
from markdown import markdown
from markdown_postprocess import postprocess

from chapter import *
from myuser import *
from mytemplate import write_template
from question import Question,list_questions
from aclass import get_student_classes
from course import Course, get_courses
from student_results import get_result

class StartPage(BaseHandler):
    def get(self):
        student = self.get_current_student()
        if not student:
            self.redirect('/')
            return
        
        classes = get_student_classes(student)
        
        if len(classes) == 1:
            self.redirect('/studentselectclass?class='+str(classes[0].key()))
            
        template_values = {
                           'classes': classes,
                           }
        write_template(self, student, 'student_start.html',template_values)

class SelectClass(BaseHandler):
    def get(self):
        student = self.get_current_student()
        if not student:
            self.redirect('/')
            return
        
        encoded_class_key = self.request.get('class')
        key = db.Key(encoded=encoded_class_key)
        memcache.set('student_class', key)
        
        self.redirect('/studentcoursespage')

class CoursesPage(BaseHandler):
    def get(self):
        student = self.get_current_student()
        if not student:
            self.redirect('/')
            return
        
        classes = get_student_classes(student)
        clss = memcache.get('student_class')
        if not clss:
            self.redirect('/')
            
        courses = get_courses(clss)
        if len(courses) == 1:
            self.redirect('/studentcoursepage?course='+str(courses[0].key()))
        
        template_values = {
                           'courses': courses,
                           }
        write_template(self, student, 'student_courses.html',template_values)

class CoursePage(BaseHandler):
    """
    Open page showing single course.
    URL: /studentcoursepage?key=<course_key>
    """
    def get(self):
        user = self.get_current_student()
        if not user:
            self.redirect('/')
            return
            
        key = db.Key(encoded=self.request.get('course'))
        course = Course.get(key)
        chapters = []
        chapter_keys = []
        for q in course.chapters:
            chapter = Chapter.get(q)
            if chapter:
                chapters.append(chapter)
                chapter_keys.append(str(chapter.key()))
        
        goto = self.request.get("goto")
        if goto == None or goto == '':
            goto = '/'
        
        template_values = {'course': course,
                           'chapters': chapters,
                           'chapter_keys': chapter_keys,
                           'goto': goto,
                           }
        write_template(self, user, 'student_course.html', template_values)

class ChapterPage(BaseHandler):
    def get(self):
        user = self.get_current_student()
        if not user:
            self.redirect('/')
            return
        
        encoded_chapter_key = self.request.get('chapter')
        chapter, encoded_chapter_key = get_chapter_by_encoded_key(encoded_chapter_key)
        
        encoded_course_key = self.request.get('course')
        course = Course.get(db.Key(encoded=encoded_course_key))
        
        if not course.has_chapter(chapter):
            self.redirect('/studentcoursepage?course='+encoded_course_key)
        
        subchapters = chapter.subchapters()
        subchapters_empty = len(subchapters) == 0
        parents = list_parents(chapter)
        parents.reverse()
        
        if chapter.text != None:
            chapter_formatted_text = markdown(chapter.text,safe_mode='escape')
            chapter_formatted_text = postprocess(chapter_formatted_text)
        else:
            chapter_formatted_text = ''
            
        questions = list_questions(chapter)
        for q in questions:
            q.result = get_result(user,q)
        has_questions = len(questions) > 0
        
        template_values = {
                           'subchapters': subchapters,
                           'subchapters_empty': subchapters_empty,
                           'parents' : parents,
                           'chapter_formatted_text' : chapter_formatted_text,
                           'questions' : questions,
                           'has_questions' : has_questions,
                           'course' : course,
                           }
        
        add_chapter_values(template_values, chapter)
        
        write_template(self, user, 'student_chapter.html',template_values)
