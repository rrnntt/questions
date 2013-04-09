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

def delete_edit_question_list():
    qlist = memcache.get('question_list')
    if qlist != None:
        memcache.delete('question_list')
        qlist.delete()

def create_question_list(name):
    qlist = QuestionList()
    qlist.name = name
    qlist.put()
    return qlist

def get_question_list(parent):
    query = QuestionList.all().ancestor(parent)
    qlist = query.fetch(1000)
    return qlist
