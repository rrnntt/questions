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

def list_visible_chapters(user, parent = None):
    """Retrieve from the datastore chapters visible to a user"""
    if parent:
        parent_key = parent.key()
    else:
        parent_key = root_key()
    chapter_query = Chapter.all().ancestor(parent_key).order('title')
    all_chapters = chapter_query.fetch(1000)
    chapters = []
    for chapter in all_chapters:
        if chapter.isVisible(user) and chapter.parent_key() == parent_key:
            chapters.append(chapter)
    return chapters

class AddChapterPage(webapp2.RequestHandler):
    def get(self):

        user = get_current_user()
        if not user:
            self.redirect('/')
        
        encoded_chapter_key = self.request.get('chapter')
        if encoded_chapter_key == 'root':
            chapter_key = root_key()
            encoded_chapter_key = str(chapter_key)
            chapter = None
        else:
            #raise Exception(encoded_chapter_key+' '+len(encoded_chapter_key))
            chapter_key = db.Key(encoded=encoded_chapter_key)
            chapter = Chapter.get(chapter_key)
            
        template_values = {
                           'chapter': chapter,
                           'chapter_key':encoded_chapter_key,
                           }
        
        write_template(self, user, 'add_chapter.html',template_values)
        
class AddChapter(webapp2.RequestHandler):
    def post(self):

        user = get_current_user()
        if not user:
            self.redirect('/')
        
        root = root_key()
        encoded_parent_key = self.request.get('parent')
        if encoded_parent_key == 'root':
            parent_key = root
        else:
            parent_key = db.Key(encoded=encoded_parent_key)
        
        title = self.request.get('title')
            
        if len(title) > 0:
            chapter = Chapter(parent=parent_key)
            chapter.authors.append(user.nickname())
            chapter.title = title
            chapter.put()
        
        if parent_key == root:
            self.redirect('/')
        else:
            self.redirect('/chapterpage?chapter='+str(chapter.key()))
            
class ChapterPage(webapp2.RequestHandler):
    def get(self):
        user = get_current_user()
        if not user:
            self.redirect('/')
        
        encoded_chapter_key = self.request.get('chapter')
        chapter = Chapter.get(db.Key(encoded=encoded_chapter_key))
        subchapters = list_visible_chapters(user, chapter)
        
        subchapters_empty = len(subchapters) > 0
        
        template_values = {
                           'chapter': chapter,
                           'subchapters': subchapters,
                           'subchapters_empty': subchapters_empty,
                           }
        
        write_template(self, user, 'chapter.html',template_values)
        
class DeleteChapter(webapp2.RequestHandler):
    def post(self):
        
        user = get_current_user()
        if not user:
            self.redirect('/')
        
        encoded_chapter_key = self.request.get('chapter')
        chapter = Chapter.get(db.Key(encoded=encoded_chapter_key))
        
        if not chapter.canEdit(user):
            self.redirect('/')
            
        chapter.delete()
        
        
        
