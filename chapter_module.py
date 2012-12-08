import webapp2
from google.appengine.ext import db
from myuser import *
import mytemplate

"""
Chapters are a way of organising questions. A chapter may either include other
chapters or questions.
"""

class Chapter(db.Model):
    """A chapter"""
    title = db.StringProperty()
    authors = db.StringListProperty()
    students = db.StringListProperty()
    
    def isVisible(self,user):
        """Check if the chapter is visile to a user"""
        if len(self.students) == 0 or user.isAdmin():
            return True
        user_name = user.nickname()
        return (user_name in self.students) or (user_name in self.authors)

    def canEdit(self,user):
        """Check if a user can edit this chapter"""
        return (user.nickname() in self.authors) or user.isAdmin()
    
def root_key():
    """Constructs a Datastore key for a root chapter."""
    return db.Key.from_path('Chapter', 'root')

def list_visible_chapters(user):
    """Retrieve from the datastore root chapters visible to a user"""
    chapter_query = Chapter.all().ancestor(root_key()).order('title')
    all_chapters = chapter_query.fetch(1000)
    chapters = []
    for chapter in all_chapters:
        if chapter.isVisible(user):
            chapters.append(chapter)
    return chapters

class AddChapterPage(webapp2.RequestHandler):
    def get(self):

        user = get_current_user()
        if not user:
            self.redirect('/')
        
        chapter_key = self.request.get('chapter')
        if chapter_key == 'root':
            chapter_key = root_key()
        
        write_template(self, user, 'add_chapter.html',{'chapter_key':chapter_key})
        
class AddChapter(webapp2.RequestHandler):
    def post(self):

        user = get_current_user()
        if not user:
            self.redirect('/')
        
        chapter_key = self.request.get('parent')
        if chapter_key == 'root':
            chapter_key = root_key()
        
        self.redirect('/addchapterpage?parent='+chapter_key)
        
