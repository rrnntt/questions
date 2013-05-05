import webapp2
from base_handler import BaseHandler
from rest import RESTHandlerClass
from question_list import *
from mytemplate import write_template
from question import Question
from aclass import get_teacher_classes, Class

class QuestionListRESTHandler(RESTHandlerClass):
    def __init__(self, request=None, response=None):
        RESTHandlerClass.__init__(self, request, response)
        self.ModelClass = QuestionList
        self.required = ['name']
        self.parent_required = True
        self.cache_key = 'question_list'
        
    def convert(self,field, value):
        if field == 'questions':
            qlist = []
            for v in value:
                key = db.Key(encoded = v)
                qlist.append(key)
            return qlist
        
        return RESTHandlerClass.convert(self, field, value)
        
class QuestionListPage(BaseHandler):
    """
    Open page showing single question list.
    URL: /questionlistpage?key=<question_list_key>&edit=<true|false>
    """
    def get(self):
        user = self.get_current_user()
        if not user:
            self.redirect('/')
            return
            
        key = db.Key(encoded=self.request.get('key'))
        qlist = QuestionList.get(key)
        questions = []
        question_keys = []
        for q in qlist.questions:
            question = Question.get(q)
            if question:
                questions.append(question)
                question_keys.append(str(question.key()))
        
        edit = self.request.get("edit")
        if edit == 'true' and user.isTeacher():
            edit = True
            class_list = get_teacher_classes(user)
            start_edit_question_list(qlist)
        else:
            edit = False
            class_list = []
            
        goto = self.request.get("goto")
        if goto == None or goto == '':
            goto = '/'
        
        template_values = {'qlist': qlist,
                           'questions': questions,
                           'question_keys': question_keys,
                           'edit': edit,
                           'class_list': class_list,
                           'goto': goto,
                           }
        write_template(self, user, 'question_list.html', template_values)
                
class SaveQuestionList(BaseHandler):
    """
    Open page showing single question list.
    URL: /savequestionlist?key=<question_list_key>&class=<aclass_key>
    """
    def get(self):
        user = self.get_current_user()
        if not user:
            self.redirect('/')
            return
            
        key = db.Key(encoded=self.request.get('key'))
        qlist = QuestionList.get(key)
        class_key = db.Key(encoded=self.request.get('class'))
        
        # if class is different copy list to the new class
        if class_key != qlist.parent_key():
            aclass = Class.get(class_key)
            newList = QuestionList(parent=aclass)
            newList.name = qlist.name
            newList.questions = qlist.questions
            newList.put()
            
        stop_edit_question_list()
        
        self.redirect('/')

class CancelEditQuestionList(BaseHandler):
    """
    Cancel list editing and remove it from shopping list.
    URL: /cancelquestionlist?goto=<url>
    """
    def get(self):
        user = self.get_current_user()
        if not user:
            self.redirect('/')
            return
            
        goto = self.request.get("goto")
        if goto == None or goto == '':
            goto = '/'
        
        stop_edit_question_list()
        
        self.redirect(goto)

class DeleteEditQuestionList(BaseHandler):
    """
    Delete list editing and remove it from shopping list.
    URL: /deletequestionlist?goto=<url>
    """
    def get(self):
        user = self.get_current_user()
        if not user:
            self.redirect('/')
            return
            
        qlist = get_edit_question_list()
        if qlist != None:
            qlist.delete()
        
        goto = self.request.get("goto")
        if goto == None or goto == '':
            goto = '/'
        
        stop_edit_question_list()
        
        self.redirect(goto)

class CreateQuestionList(BaseHandler):
    """
    Open page showing single question list.
    URL: /savequestionlist?key=<question_list_key>&class=<aclass_key>
    """
    def get(self):
        user = self.get_current_user()
        if not user:
            self.redirect('/')
            return
            
        parent_key = db.Key(encoded=self.request.get('parent'))
        qlist = create_question_list(parent_key)
        start_edit_question_list(qlist)
        
        goto = self.request.get('goto')
        if goto == None and goto == '':
            goto = '/'
        
        self.redirect(goto)
