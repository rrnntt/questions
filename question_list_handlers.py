import webapp2
from rest import MemcachedRESTHandler
from question_list import *
from mytemplate import write_template
from myuser import get_current_teacher, get_current_user
from question import Question
from aclass import get_teacher_classes, Class

class QuestionListRESTHandler(MemcachedRESTHandler):
    def __init__(self, request=None, response=None):
        MemcachedRESTHandler.__init__(self, request, response)
        self.ModelClass = QuestionList
        self.required = ['name']
        self.cache_key = 'question_list'
        
    def convert(self,field, value):
        if field == 'questions':
            qlist = []
            for v in value:
                key = db.Key(encoded = v)
                qlist.append(key)
            return qlist
        
        return MemcachedRESTHandler.convert(self, field, value)
        
class QuestionListPage(webapp2.RequestHandler):
    """
    Open page showing single question list.
    URL: /questionlistpage?key=<question_list_key>&edit=<true|false>
    """
    def get(self):
        user = get_current_user()
        if not user:
            self.redirect('/')
            return
            
        key = db.Key(encoded=self.request.get('key'))
        qlist = QuestionList.get(key)
        questions = []
        for q in qlist.questions:
            question = Question.get(q)
            if question:
                questions.append(question)
        
        edit = self.request.get("edit")
        if edit == 'true' and user.isTeacher():
            edit = True
            class_list = get_teacher_classes(user)
        else:
            edit = False
            class_list = []
            
        goto = self.request.get("goto")
        if goto == None or goto == '':
            goto = '/'
        
        template_values = {'qlist': qlist,
                           'questions': questions,
                           'edit': edit,
                           'class_list': class_list,
                           'goto': goto,
                           }
        write_template(self, user, 'question_list.html', template_values)
                
class SaveQuestionList(webapp2.RequestHandler):
    """
    Open page showing single question list.
    URL: /savequestionlist?key=<question_list_key>&class=<aclass_key>
    """
    def get(self):
        user = get_current_user()
        if not user:
            self.redirect('/')
            return
            
        key = db.Key(encoded=self.request.get('key'))
        qlist = QuestionList.get(key)
        key = db.Key(encoded=self.request.get('class'))
        aclass = Class.get(key)
        newList = QuestionList(parent=aclass)
        newList.name = qlist.name
        newList.questions = qlist.questions
        newList.put()
        delete_edit_question_list()
        
        self.redirect('/')
