import webapp2
from google.appengine.ext import db

from rest import RESTHandlerClass
from base_handler import BaseHandler
from course import Course, create_course
from mytemplate import write_template
from chapter_module import Chapter
from aclass import get_teacher_classes, Class

class CourseRESTHandler(RESTHandlerClass):
    def __init__(self, request=None, response=None):
        RESTHandlerClass.__init__(self, request, response)
        self.ModelClass = Course
        self.required = ['name']
        self.parent_required = True
        self.cache_key = 'course'
        
    def convert(self,field, value):
        if field == 'chapters':
            qlist = []
            for v in value:
                key = db.Key(encoded = v)
                qlist.append(key)
            return qlist
        
        return RESTHandlerClass.convert(self, field, value)
        
class CourseHandler(BaseHandler):
    def get_edit_course(self):
        """
        Get the cached Course which is being edited (in "shopping basket")
        """
        if 'course' in self.session:
            key = self.session['course']
            return db.get( key )
        return None
    
    def stop_edit_course(self):
        if 'course' in self.session:
            del self.session['course']
    
    def start_edit_course(self, course):
        self.session['course'] = str(course.key())
    
class CoursePage(CourseHandler):
    """
    Open page showing single course.
    URL: /coursepage?key=<course_key>&edit=<true|false>
    """
    def get(self):
        user = self.get_current_user()
        if not user:
            self.redirect('/')
            return
            
        key = db.Key(encoded=self.request.get('key'))
        course = Course.get(key)
        chapters = []
        chapter_keys = []
        for q in course.chapters:
            chapter = Chapter.get(q)
            if chapter:
                chapters.append(chapter)
                chapter_keys.append(str(chapter.key()))
        
        edit = self.request.get("edit")
        if edit == 'true' and user.isTeacher():
            edit = True
            class_list = get_teacher_classes(user)
            self.start_edit_course(course)
        else:
            edit = False
            class_list = []
            
        goto = self.request.get("goto")
        if goto == None or goto == '':
            goto = '/'
        
        template_values = {'course': course,
                           'chapters': chapters,
                           'chapter_keys': chapter_keys,
                           'edit': edit,
                           'class_list': class_list,
                           'goto': goto,
                           }
        write_template(self, user, 'course.html', template_values)
                
class SaveCourse(CourseHandler):
    """
    Save course and remove it from shopping list.
    URL: /savecourse?key=<course_key>&class=<aclass_key>
    """
    def get(self):
        user = self.get_current_user()
        if not user:
            self.redirect('/')
            return
            
        key = db.Key(encoded=self.request.get('key'))
        course = Course.get(key)
        class_key = db.Key(encoded=self.request.get('class'))
        
        goto = self.request.get("goto")
        if goto == None or goto == '':
            goto = '/'
        
        # if class is different copy list to the new class
        if class_key != course.parent_key():
            aclass = Class.get(class_key)
            newCourse = Course(parent=aclass)
            newCourse.name = course.name
            newCourse.chapters = course.chapters
            newCourse.count_questions()
            newCourse.put()
            
        self.stop_edit_course()
        
        self.redirect(goto)

class CancelEditCourse(CourseHandler):
    """
    Cancel course editing and remove it from shopping list.
    URL: /cancelcourse?goto=<url>
    """
    def get(self):
        user = self.get_current_user()
        if not user:
            self.redirect('/')
            return
            
        goto = self.request.get("goto")
        if goto == None or goto == '':
            goto = '/'
        
        self.stop_edit_course()
        
        self.redirect(goto)

class DeleteEditCourse(CourseHandler):
    """
    Delete course editing and remove it from shopping list.
    URL: /deletecourse?goto=<url>
    """
    def get(self):
        user = self.get_current_user()
        if not user:
            self.redirect('/')
            return
            
        course = self.get_edit_course()
        if course != None:
            course.delete()
            
        goto = self.request.get("goto")
        if goto == None or goto == '':
            goto = '/'
        
        self.stop_edit_course()
        
        self.redirect(goto)

class CreateCourse(CourseHandler):
    """
    Create new course.
    URL: /createcourse?parent=<parent_key>&goto=<url>
    """
    def get(self):
        user = self.get_current_user()
        if not user:
            self.redirect('/')
            return
            
        parent_key = db.Key( encoded=self.request.get('parent') )
        course = create_course(parent_key)
        self.start_edit_course(course)
        
        goto = self.request.get('goto')
        if goto == None and goto == '':
            goto = '/'
        
        self.redirect(goto)
