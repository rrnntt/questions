from google.appengine.ext import db
from google.appengine.api import memcache

class QuestionList(db.Model):
    # Name/Title of the list (e.g. Test #2, Homework 01/02/13, ...)
    name = db.StringProperty()
    # Qeuestions in this list 
    questions = db.ListProperty(db.Key)
    
    def size(self):
        return len(self.questions)

def get_edit_question_list():
    """
    Get the cached QuestionList which is being edited (in "shopping basket")
    """
    return memcache.get('question_list')

def create_question_list(name):
    qlist = QuestionList()
    qlist.name = name
    qlist.put()
    return qlist
