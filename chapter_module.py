#import logging
import json

from base_handler import BaseHandler
from chapter import *
from myuser import *
from mytemplate import write_template
from question import list_questions, Question
from mymarkdown import mymarkdown,update_links

"""
Chapters are a way of organising questions. A chapter may either include other
chapters or questions.
"""

def set_chapter_text(chapter, text, save=False):
    """Parse the new text and correct if needed.
    
    Consider input text to have Markdown format.
    - Image names in reference links need to have urls.
    """
    chapter.text = update_links(chapter, text)
    chapter.refresh = False
    if save:
        chapter.put()


def set_question_text(chapter, question, text, save=False):
    """Parse the new text and correct if needed.
    
    Consider input text to have Markdown format.
    - Image names in reference links need to have urls.
    """
    question.text = update_links(chapter, text)
    question.refresh = False
    if save:
        question.put()
        
def refresh_chapter(chapter):
    chapter.refresh = True
    chapter.put()
    query = Question.all().filter('chapter =', chapter)
    for q in query.run():
        q.refresh = True
        q.put
    query = Chapter.all().ancestor(chapter.key())
    for c in query.run():
        if c  != chapter:
            refresh_chapter(c)


###########################################################################
#     Request handlers
###########################################################################
            
class ChapterPage(BaseHandler):
    def get(self):
        user = self.get_current_user()
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
            if chapter.refresh:
                text = chapter.text
                set_chapter_text(chapter, text, True)
            chapter_formatted_text = mymarkdown(chapter.text)
        else:
            chapter_formatted_text = ''
            
        questions = list_questions(chapter)
        for q in questions:
            if q.refresh:
                text = q.text
                set_question_text(chapter, q, text, True)
            q.formatted_text = mymarkdown(q.text)
        
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
        
class EditChapterPage(BaseHandler):
    def get(self):

        user = self.get_current_user()
        if not user:
            self.redirect('/')
            return
        
        encoded_chapter_key = self.request.get('chapter')
        chapter, encoded_chapter_key = get_chapter_by_encoded_key(encoded_chapter_key)

        questions = list_questions(chapter)
        for q in questions:
            if q.refresh:
                text = q.text
                set_question_text(chapter, q, text, True)
            q.formatted_text = mymarkdown(q.text)
        
        has_questions = len(questions) > 0
        has_text = chapter.text and len(chapter.text) > 0
        template_values = {
                           'questions' : questions,
                           'has_questions' : has_questions,
                           'has_text': has_text,
                           }
        add_chapter_values(template_values, chapter)
        template_values['title'] = 'Edit chapter ' + chapter.title
        
        write_template(self, user, 'chapter_edit.html',template_values)
        
###########################################################################
#     Chapters
###########################################################################
class Chapters(BaseHandler):
    """Implements REST service for managing chapters"""
    def put(self,Id):
        """Save a chapter with key == Id"""
        #raise Exception(self.request.arguments())
        chapter,ekey = get_chapter_by_encoded_key(Id)
        if chapter:
            jsn = json.decoder.JSONDecoder()
            model = jsn.decode( self.request.get('model'))
            #raise Exception(model[0])
            if not 'parent_key' in model:
                self.response.out.write('error')
                return
            chapter.title = model['title']
            if 'text' in model:
                set_chapter_text(chapter, model['text'])
            chapter.put()
        else:
            raise Exception('Saving of chapter failed')

    def post(self,Id=None):
        """Create new chapter instance and retirn its id which is its key"""
        user = self.get_current_user()
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
            
        jsn = json.decoder.JSONDecoder()
        model = jsn.decode( self.request.get('model'))
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

