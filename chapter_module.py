import webapp2
from google.appengine.ext import db
import simplejson
from myuser import *
import mytemplate
from question import Question

"""
Chapters are a way of organising questions. A chapter may either include other
chapters or questions.
"""

###########################################################################
#     Chapter model class
###########################################################################

class Chapter(db.Model):
    """A chapter"""
    title = db.StringProperty()
    authors = db.ListProperty(db.Key)
    text = db.TextProperty()
    
    def canEdit(self,user):
        """Check if a user can edit this chapter"""
        return self.key() == root_key() or user.key() in self.authors
    
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
        if len(self.authors) == 1:
            return
        k = author.key()
        if not k in self.authors:
            return
        i = self.authors.index(k)
        del self.authors[i:i+1]
        
        
def create_chapter(parent_chapter, author, title):
    parent_key = parent_chapter
    if not isinstance( parent_key, db.Key ):
        parent_key = parent_key.key()
    chapter = Chapter(parent=parent_key)
    chapter.authors.append(author.key())
    chapter.title = title
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
    
def list_questions(chapter):
    parent_key = chapter.key()
    query = Question.all().ancestor(parent_key)
    # try to fetch all of them. I hope 1000 is a large enogh number.
    all_qs = query.fetch(1000)
    qs = []
    i = 1
    for q in all_qs:
        if q.parent_key() == parent_key:
            qs.append(q)
            stri = str(i)
            i += 1
            if q.title != stri:
                q.title = stri
                q.put()
    return qs

###########################################################################
#     Request handlers
###########################################################################
            
class ChapterPage(webapp2.RequestHandler):
    def get(self):
        user = get_current_user()
        if not user:
            self.redirect('/')
            return
        
        encoded_chapter_key = self.request.get('chapter')
        
        chapter, encoded_chapter_key = get_chapter_by_encoded_key(encoded_chapter_key)
        subchapters = list_edit_chapters(user, chapter)
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
                           }
        
        add_chapter_values(template_values, chapter)
        
        write_template(self, user, 'chapter.html',template_values)
        
class AddChapterPage(webapp2.RequestHandler):
    def get(self):

        user = get_current_user()
        if not user:
            self.redirect('/')
            return
        
        encoded_chapter_key = self.request.get('chapter')
        chapter, encoded_chapter_key = get_chapter_by_encoded_key(encoded_chapter_key)
        template_values = {}
        add_chapter_values(template_values, chapter)
        
        write_template(self, user, 'add_chapter.html',template_values)
        
class EditChapterPage(webapp2.RequestHandler):
    def get(self):

        user = get_current_user()
        if not user:
            self.redirect('/')
            return
        
        encoded_chapter_key = self.request.get('chapter')
        chapter, encoded_chapter_key = get_chapter_by_encoded_key(encoded_chapter_key)

        questions = list_questions(chapter)
        has_questions = len(questions) > 0
        template_values = {
                           'questions' : questions,
                           'has_questions' : has_questions,
                           }
        add_chapter_values(template_values, chapter)
        template_values['title'] = 'Edit chapter ' + chapter.title
        
        write_template(self, user, 'chapter_edit.html',template_values)
        
###########################################################################
#     Chapters
###########################################################################
class Chapters(webapp2.RequestHandler):
    """Implements REST service for managing chapters"""
    def put(self,Id):
        """Save a chapter with key == Id"""
        #raise Exception(self.request.arguments())
        chapter,ekey = get_chapter_by_encoded_key(Id)
        if chapter:
            json = simplejson.decoder.JSONDecoder()
            model = json.decode( self.request.get('model'))
            #raise Exception(model[0])
            if not 'parent_key' in model:
                self.response.out.write('error')
                return
            chapter.title = model['title']
            if 'text' in model:
                chapter.text = model['text']
            chapter.put()
        else:
            raise Exception('Saving of chapter failed')

    def post(self,Id=None):
        """Create new chapter instance and retirn its id which is its key"""
        user = get_current_user()
        if not user:
            self.redirect('/')
            return
            
        #raise Exception(self.request.get('_method'))
        httpMethod = self.request.get('_method')
        if httpMethod == 'PUT':
            self.put(Id)
            return
        if httpMethod == 'DELETE':
            self.delete(Id)
            return
        if httpMethod == 'GET':
            raise Exception('GET not implemented')
            return
            
        json = simplejson.decoder.JSONDecoder()
        model = json.decode( self.request.get('model'))
        #raise Exception(model[0])
        if not 'parent_key' in model:
            self.response.out.write('error')
        if not 'title' in model:
            self.response.out.write('error')
        
        root = root_key()
        encoded_parent_key = model['parent_key']
        if encoded_parent_key == 'root':
            parent_key = root
        else:
            parent_key = db.Key(encoded=encoded_parent_key)
        
        title = model['title']
            
        if len(title) > 0:
            chapter = Chapter(parent=parent_key)
            chapter.authors.append(user.key())
            chapter.title = title
            chapter.put()
        else:
            self.response.out.write('error')
            return
        
        self.response.out.write('{"id":"'+str(chapter.key())+'"}')

    def delete(self, Id):
        """Delete a chapter with key == Id"""
        chapter,ekey = get_chapter_by_encoded_key(Id)
        if chapter:
            chapter.deleteAll()
        else:
            raise Exception('Deleting of chapter failed')

