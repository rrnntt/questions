#import logging
#import webapp2
#from google.appengine.ext import db
import json

from base_handler import BaseHandler
from mytemplate import write_template
from myuser import *
from question import *
from chapter_module import get_chapter_by_encoded_key
from student_results import save_result
from mymarkdown import update_links

###########################################################################
#     Questions pages
###########################################################################

class EditQuestionPage(BaseHandler):
    def get(self):

        user = self.get_current_user()
        if not user:
            self.redirect('/')
            return
        
        encoded_chapter_key = self.request.get('chapter')
        chapter, encoded_chapter_key = get_chapter_by_encoded_key(encoded_chapter_key)
        
        question_key = self.request.get('question')
        if question_key == 'new':
            question = Question.create(chapter)
        else:
            question = Question.get(db.Key(encoded=question_key))
        question_key = question.key()
            
        template_values = {
                           'chapter' : chapter,
                           'question' : question,
                           }
        template_values['title'] = 'Edit question in ' + chapter.title
        
        write_template(self, user, 'question_edit.html',template_values)
        

###########################################################################
#     Questions REST interface
###########################################################################
class Questions(BaseHandler):
    """Implements REST service for managing questions"""
    def put(self,Id):
        """Save a question with key == Id"""
        #raise Exception(self.request.arguments())
        question = Question.get(db.Key(encoded = Id))

        if question:
            jsn = json.decoder.JSONDecoder()
            model = jsn.decode( self.request.get('model'))
            if 'text' in model:
                question.text = model['text']
                question.refresh = True
            if 'answer' in model:
                question.answer = model['answer']
            if 'type' in model:
                question.type = model['type']
            question.put()
            #question = Question.get(db.Key(encoded = Id))
            #logging.info('text: '+question.text)
        else:
            raise Exception('Saving of question failed')

    def post(self,Id=None):
        """Create new chapter instance and retirn its id which is its key"""
        user = self.get_current_user()
        if not user:
            self.redirect('/')
            return
            
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

        if not 'text' in model or not 'answer' in model or not 'chapter' in model:
            self.response.out.write('error')
            return
        
        text = model['text']
        
        if len(text) > 0:
            chapter_key = db.Key(encoded=model['chapter'])
            question = Question.create(chapter_key)
            question.text = text
            question.answer = model['answer']
            question.put()
        else:
            self.response.out.write('error')
            return
        
        self.response.out.write('{"id":"'+str(question.key())+'"}')

    def delete(self, Id):
        """Delete a chapter with key == Id"""
        question = Question.get(db.Key(encoded = Id))
        if question:
            question.delete()
        else:
            raise Exception('Deleting of question failed')

class Answer(BaseHandler):
    """Implements REST service for receiving answers"""
    def put(self,Id):
        question = Question.get(db.Key(encoded = Id))
        student = self.get_current_student()

        if question:
            jsn = json.decoder.JSONDecoder()
            model = jsn.decode( self.request.get('model'))
            if not 'answer' in model:
                raise Exception('Chacking answer failed')
            
            answer = model['answer']
            result = question.check_answer(answer)
            save_result(student, question, answer, result) 
            self.response.out.write('{"res":"' + result + '"}')

    def post(self,Id=None):

        user = self.get_current_user()
        if not user:
            self.redirect('/')
            return
            
        httpMethod = self.request.get('_method')
        if httpMethod == 'PUT':
            self.put(Id)
            return
        
        self.redirect('/')
