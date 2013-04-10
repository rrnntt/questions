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

def stop_edit_question_list():
    memcache.delete('question_list')

def start_edit_question_list(qlist):
    memcache.add('question_list',qlist)

def create_question_list(clss, name = 'new'):
    qlist = QuestionList(parent=clss)
    qlist.name = name
    qlist.put()
    return qlist

def get_question_list(parent):
    """
    Get all question lists belonging to a parent (eg Class)
    """
    query = QuestionList.all().ancestor(parent)
    qlist = query.fetch(1000)
    return qlist
