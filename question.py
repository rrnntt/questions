from google.appengine.ext import db
from google.appengine.ext.db import polymodel

class Question(polymodel.PolyModel):
    title = db.StringProperty()
    text = db.TextProperty()
    answer = db.TextProperty()
    type = db.StringProperty() # numeric, text
    solution = db.TextProperty() # ? should it be a model itself ?
    
    def get_answer(self):
        return self.answer
    
class CompositeQuestion(Question):
    questions = db.ListProperty(db.Key)
    
    def add_question(self, q):
        self.questions.append(q.key())
        self.put()

    def __getitem__(self, i):
        k = self.questions[i]
        return Question.get(k)
    
    def __len__(self):
        return len(self.questions)
    
    def get_answer(self):
        ans = []
        n = self.__len__()
        for i in range(n):
            ans.append(self[i].get_answer())
        return ans
