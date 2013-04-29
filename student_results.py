import webapp2
from google.appengine.ext import db
from question import Question
from myuser import MyUser

class StudentResult(db.Model):
    """Result of student answering a question"""
    student = db.ReferenceProperty(MyUser)
    question = db.ReferenceProperty(Question)
    result = db.BooleanProperty()


def save_result(student,question,status):
    # find and delete any previous results of same student and same question
    query = StudentResult.all().filter('student =', student).filter('question =', question)
    for res in query.run():
        res.delete()
    
    result = StudentResult()
    result.student = student
    result.question = question
    result.result = status
    result.put()

def passed(student,question):
    query = StudentResult.all().filter('student =', student.key()).filter('question =', question).filter('result =', True)
    return query.count() != 0 
