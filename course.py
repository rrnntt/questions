from google.appengine.ext import db
from google.appengine.api import memcache

class Course(db.Model):
    # Name/Title of the course 
    name = db.StringProperty()
    # Chapters in this course 
    chapters = db.ListProperty(db.Key)
    
    def size(self):
        return len(self.chapters)

def get_edit_course():
    """
    Get the cached course which is being edited (in "shopping basket")
    """
    return memcache.get('course')

def stop_edit_course():
    memcache.delete('course')

def start_edit_course(course):
    memcache.add('course',course)

def create_course(clss, name = 'new'):
    course = Course(parent=clss)
    course.name = name
    course.put()
    return course

def get_courses(parent):
    """
    Get all courses belonging to a parent (eg Class)
    """
    query = Course.all().ancestor(parent)
    course = query.fetch(1000)
    return course
