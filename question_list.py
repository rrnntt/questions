from google.appengine.ext import db

class QuestionList(db.Model):
    # Name/Title of the list (e.g. Test #2, Homework 01/02/13, ...)
    name = db.StringProperty()
    # Qeuestions in this list 
    questions = db.ListProperty(db.Key)
