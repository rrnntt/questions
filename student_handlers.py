from google.appengine.api import memcache
#import json

from chapter import *
from myuser import *
from mytemplate import write_template
from question import Question
from aclass import get_student_classes
from course import Course, get_courses

class StartPage(webapp2.RequestHandler):
    def get(self):
        student = get_current_student()
        if not student:
            self.redirect('/')
            return
        
        classes = get_student_classes(student)
        template_values = {
                           'classes': classes,
                           }
        write_template(self, student, 'student_start.html',template_values)

class SelectClass(webapp2.RequestHandler):
    def get(self):
        student = get_current_student()
        if not student:
            self.redirect('/')
            return
        
        encoded_class_key = self.request.get('class')
        key = db.Key(encoded=encoded_class_key)
        memcache.set('student_class', key)
        
        self.redirect('/studentcoursespage')

class CoursesPage(webapp2.RequestHandler):
    def get(self):
        student = get_current_student()
        if not student:
            self.redirect('/')
            return
        
        classes = get_student_classes(student)
        clss = memcache.get('student_class')
        if not clss:
            self.redirect('/')
            
        courses = get_courses(clss)
        
        template_values = {
                           'courses': courses,
                           }
        write_template(self, student, 'student_courses.html',template_values)

class CoursePage(webapp2.RequestHandler):
    """
    Open page showing single course.
    URL: /studentcoursepage?key=<course_key>
    """
    def get(self):
        user = get_current_student()
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

class ChapterPage(webapp2.RequestHandler):
    def get(self):
        user = get_current_student()
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
            chapter_formatted_text = chapter.text
        else:
            chapter_formatted_text = ''
            
        questions = list_questions(chapter)
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