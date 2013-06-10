#import logging
from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from chapter import Chapter

class Question(polymodel.PolyModel):
    chapter = db.ReferenceProperty(Chapter)
    title = db.StringProperty()
    text = db.TextProperty()
    refresh = db.BooleanProperty()
    id = db.IntegerProperty()
    answer = db.TextProperty()
    type = db.StringProperty()   # numeric, formula, text
    solution = db.TextProperty() # ? should it be a model itself ?
    
    def get_answer(self):
        return self.answer
    
    def check_answer(self, answer):
        """ Automatic answer check. For open-ended questions return 'unmarked'.
        Return a value of StudentResult.result propery: 'correct', 'wrong', or 'unmarked' """
        if self.is_open_ended():
            return 'unmarked'
        res = self.get_answer() == answer
        if res:
            return 'correct'
        return 'wrong'
    
    def is_open_ended(self):
        return self.answer == None or len(self.answer) == 0
    
    @classmethod
    def create(cls, chapter, typ = 'numeric'):
        question = Question(parent=chapter)
        question.chapter = chapter
        question.title = 'new'
        question.text = ''
        # if answer isn't set then it's an open-ended question
        question.answer = None 
        question.type = typ
        question.id = 1000000
        question.refresh = True
        question.put()
        return question    

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

def list_questions(chapter):
    query = Question.all().filter('chapter =', chapter).order('id')
    qs = []
    i = 0
    for q in query.run():
        qs.append(q)
        i += 1
        if q.id != i:
            q.id = i
            q.title = str(i)
            q.put()
    return qs

def count_questions(chapter):
    query = Question.all().filter('chapter =', chapter)
    return query.count()
    
