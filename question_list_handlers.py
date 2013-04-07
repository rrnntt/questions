import webapp2
from rest import RESTHandlerClass
from question_list import *
from mytemplate import write_template
from myuser import get_current_user
from question import Question

class QuestionListRESTHandler(RESTHandlerClass):
    def __init__(self, request=None, response=None):
        RESTHandlerClass.__init__(self, request, response)
        self.ModelClass = QuestionList
        self.required = ['name']
        
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
                