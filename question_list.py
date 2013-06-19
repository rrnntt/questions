from google.appengine.ext import db
from google.appengine.api import memcache
from aclass import Class

class QuestionList(db.Model):
    # Class 
    clss = db.ReferenceProperty(Class)
    # Name/Title of the list (e.g. Test #2, Homework 01/02/13, ...)
    name = db.StringProperty()
    # Qeuestions in this list 
    questions = db.ListProperty(db.Key)
    
    def size(self):
        return len(self.questions)

    @classmethod
    def create(cls, clss, name = 'new'):
        qlist = QuestionList(parent=clss)
        qlist.clss = clss
        qlist.name = name
        qlist.put()
        return qlist
    
    def __getitem__(self,i):
        return db.get( self.questions[i] )

def get_question_list(parent):
    """
    Get all question lists belonging to a parent (eg Class)
    """
    query = QuestionList.all().filter('clss =',parent)
    qlist = query.fetch(1000)
    return qlist
