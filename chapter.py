#import webapp2
from google.appengine.ext import db
#from question import Question
from myuser import MyUser
#import re


###########################################################################
#     Chapter model class
###########################################################################

class Chapter(db.Model):
    """A chapter"""
    title = db.StringProperty()
    owner = db.ReferenceProperty(MyUser)
    authors = db.ListProperty(db.Key)
    text = db.TextProperty()
    refresh = db.BooleanProperty()
    
    def canEdit(self,user):
        """Check if a user can edit this chapter"""
        return self.key() == root_key() or user.key() in self.authors
    
    def isOwner(self,user):
        """Check if a user owns this chapter"""
        return user.key() == self.owner.key()
    
    def deleteAll(self):
        """Delete this chater and all child chapters recursively"""
        chapter_query = Chapter.all().ancestor(self.key())
        all_chapters = chapter_query.fetch(1000)
        for chapter in all_chapters:
            chapter.delete()
        self.delete()
        
    def get_author(self,i = None):
        if i == None:
            i = 0
        author = MyUser.get( self.authors[i] )
        return author
    
    def get_author_count(self):
        return len( self.authors )
    
    def add_author(self, author):
        k = author.key()
        if k in self.authors:
            return
        self.authors.append( k )
        
    def remove_author(self, author):
        if len(self.authors) == 1 or self.isOwner(author):
            return False
        k = author.key()
        if not k in self.authors:
            return False
        i = self.authors.index(k)
        del self.authors[i:i+1]
        return True
        
    def get_author_nicknames(self):
        names = []
        for a in self.authors:
            author = db.get(a)
            names.append(author.nickname())
        return names
        
    def list_all_subchapters(self):
        query = Chapter.all().ancestor(self.key())
        return query.fetch(1000)
    
    def subchapters(self):
        query = Chapter.all().ancestor(self.key()).order('title')
        # try to fetch all of them. I hope 1000 is a large enogh number.
        all_chapters = query.fetch(1000)
        chapters = []
        # collect only direct descendants of parent chapters
        for chapter in all_chapters:
            if chapter.parent_key() == self.key():
                chapters.append(chapter)
        # return the result
        return chapters
    
    
    
def create_chapter(parent_chapter, author, title):
    parent_key = parent_chapter
    if not isinstance( parent_key, db.Key ):
        parent_key = parent_key.key()
    chapter = Chapter(parent=parent_key)
    chapter.owner = author
    chapter.authors.append(author.key())
    chapter.title = title
    chapter.refresh = True
    chapter.put()
    return chapter
    
def root_key():
    """Constructs a Datastore key for the root chapter.
    
    The root chapter is just a container for the top-level chapters. It doesn't have a title
    or text or questions, only the key.
    """
    return db.Key.from_path('Chapter', 'root')

def list_visible_chapters(user, parent = None):
    """Retrieve from the datastore chapters visible to a user.
    
    Args:
        user (MyUser): the user requestion the list.
        parent (Chapter): the parent chapter. This function returns only the immediate
            sub-chapters of parent. If parent is None the function returns the top-level
            chapters.
            
    Return: 
        A list of Chapter
    """
    if parent:
        parent_key = parent.key()
    else:
        parent_key = root_key()
    # find all descendants (sub-chapters of all levels) of parent
    chapter_query = Chapter.all().ancestor(parent_key).order('title')
    # try to fetch all of them. I hope 1000 is a large enogh number.
    all_chapters = chapter_query.fetch(1000)
    chapters = []
    # collect only visible to user and direct descendants of parent chapters
    for chapter in all_chapters:
        if chapter.canEdit(user) and chapter.parent_key() == parent_key:
            chapters.append(chapter)
    # return the result
    return chapters

def list_edit_chapters(user, parent = None):
    """Retrieve from the datastore chapters a user can edit (is an author of).
    
    Args:
        user (MyUser): the user requestion the list.
        parent (Chapter): the parent chapter. This function returns only the immediate
            sub-chapters of parent. If parent is None the function returns the top-level
            chapters.
            
    Return: 
        A list of Chapter
    """
    if parent:
        parent_key = parent.key()
    else:
        parent_key = root_key()
    # find all descendants (sub-chapters of all levels) of parent
    chapter_query = Chapter.all().ancestor(parent_key)#.order('title')
    # try to fetch all of them. I hope 1000 is a large enogh number.
    all_chapters = chapter_query.fetch(1000)
    chapters = []
    # collect only visible to user and direct descendants of parent chapters
    for chapter in all_chapters:
        if chapter.canEdit(user) and chapter.parent_key() == parent_key:
            chapters.append(chapter)
    # return the result
    return chapters

def get_chapter_by_encoded_key(encoded_key):
    """Get the chapter from datastore by its encoded key.
    
    An encoded key is the string representation of a key that can be used in URLs.
    This function is for retrieving chapters in http handlers. 
    
    Args:
        encoded_key (str): an encoded datastore key for a real chapter or string 'root'
        for the root chapter
        
    Return:
        tuple (Chapter,encoded_key). If you get the root chapter encoded_key will be real
        encoded key of the root chapter.
    """
    encoded_chapter_key = encoded_key
    # if root chapter requested get the real key for it
    if encoded_chapter_key == 'root' or encoded_chapter_key == 'None':
        chapter_key = root_key()
        encoded_chapter_key = str(chapter_key)
        chapter = Chapter.get(chapter_key)
        # in case root chapter doesn't exist yet in datastore, create and put it there
        if not chapter:
            chapter = Chapter(key_name='root')
            chapter.title = 'Root'
            chapter.put()
    else:
        # if it's a real key just get the chapter from datastore
        chapter_key = db.Key(encoded=encoded_chapter_key)
        chapter = Chapter.get(chapter_key)
    # return the result
    return chapter, encoded_chapter_key

def add_chapter_values(template_values, chapter):
        chapter_parent_key = chapter.parent_key()
        if not chapter_parent_key:
            chapter_parent_key = 'root'
        
        template_values['chapter'] = chapter
        parent_key = chapter.parent_key()
        if not parent_key:
            parent_key = 'root'
        template_values['chapter_parent_key'] = parent_key 
        
def list_parents(chapter):
    parents = []
    if chapter == None:
        return parents
    p = chapter.parent()
    while p != None:
        parents.append(p)
        p = p.parent()
    return parents
    
