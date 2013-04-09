import webapp2
from rest import MemcachedRESTHandler
from question_list import *
from mytemplate import write_template
from myuser import get_current_teacher, get_current_user
from question import Question

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
    URL: /questionlistpage?key=<question_list_key>
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
        #raise Exception('stu:'+str(len(clss)))
        template_values = {'qlist': qlist,
                           'questions': questions,
                           }
        write_template(self, user, 'question_list.html', template_values)
                
class SaveQuestionList(webapp2.RequestHandler):
    
    def get(self):
        user = get_current_teacher()
        if not user:
            self.redirect('/')
            return
        
        qlist = get_edit_question_list()
        if qlist == None:
            qlist = create_question_list('new')
            
        lst = self.request.get('questions')
        if not isinstance(lst,list):
            raise Exception('List of questions must be a list')
        
        for key in lst:
            qlist.questions.append(db.Key(encoded=key))
            
        url = self.request.get('goto')
        self.redirect(url)
    