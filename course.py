from google.appengine.ext import db
from google.appengine.api import memcache
from chapter import Chapter, root_key
from student_results import StudentResult

class Course(db.Model):
    # Name/Title of the course 
    name = db.StringProperty()
    # Chapters in this course 
    chapters = db.ListProperty(db.Key)
    # number of questions in this course
    num_questions = db.IntegerProperty()
    
    def size(self):
        return len(self.chapters)
    
    def has_chapter(self, chapter):
        """
        Check if the course has a prticular chapter
        """
        if isinstance(chapter, Chapter):
            chapter_key = chapter.key()
        else:
            chapter_key = chapter
            chapter = Chapter.get(chapter_key)
            
        if chapter_key in self.chapters:
            return True
        
        root = root_key()
        parent_chapter_key = chapter.parent_key()
        while parent_chapter_key != root and parent_chapter_key != None: 
            if parent_chapter_key in self.chapters:
                return True
            chap = Chapter.get(parent_chapter_key)
            parent_chapter_key = chap.parent_key()
            
        return False  
    
    def count_questions(self):
        n = 0
        for key in self.chapters:
            chapter = Chapter.get(key)
            n += chapter.count_questions()
        self.num_questions = n
        
    def get_progress(self,student):
        n = StudentResult.all().filter('student =',student).filter('result =',True)
        return float(n) / self.num_questions

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

def get_courses(parent_class):
    """
    Get all courses belonging to a parent Class
    """
    query = Course.all().ancestor(parent_class)
    course = query.fetch(1000)
    return course

