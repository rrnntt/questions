import webapp2
from google.appengine.ext import db
import simplejson
from mytemplate import write_template
from myuser import *
from question import *
from chapter_module import get_chapter_by_encoded_key

###########################################################################
#     Questions helper functions
###########################################################################

def create_question(chapter, typ = 'numeric'):
    question = Question(parent=chapter.key())
    question.title = 'new'
    question.text = ''
    question.answer = ''
    question.type = typ
    question.put()
    return question

###########################################################################
#     Questions pages
###########################################################################

class EditQuestionPage(webapp2.RequestHandler):
    def get(self):

        user = get_current_user()
        if not user:
            self.redirect('/')
            return
        
        encoded_chapter_key = self.request.get('chapter')
        chapter, encoded_chapter_key = get_chapter_by_encoded_key(encoded_chapter_key)
        
        question_key = self.request.get('question')
        if question_key == 'new':
            question = create_question(chapter)
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
class Questions(webapp2.RequestHandler):
    """Implements REST service for managing questions"""
    def put(self,Id):
        """Save a question with key == Id"""
        #raise Exception(self.request.arguments())
        question = Question.get(db.Key(encoded = Id))

        if question:
            json = simplejson.decoder.JSONDecoder()
            model = json.decode( self.request.get('model'))
            #raise Exception(model[0])
            if 'text' in model:
                question.text = model['text']
            if 'answer' in model:
                question.answer = model['answer']
            if 'type' in model:
                question.type = model['type']
            question.put()
        else:
            raise Exception('Saving of question failed')

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

        if not 'text' in model or not 'answer' in model or not 'chapter' in model:
            self.response.out.write('error')
            return
        
        text = model['text']
        
        if len(text) > 0:
            chapter_key = db.Key(encoded=model['chapter'])
            question = Question(parent=chapter_key)
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

