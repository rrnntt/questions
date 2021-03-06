#import webapp2
from google.appengine.ext import db
from question import Question
from myuser import MyUser

class StudentResult(db.Model):
    """Result of student answering a question"""
    student = db.ReferenceProperty(MyUser)
    question = db.ReferenceProperty(Question)
    answer = db.TextProperty()
    solution = db.TextProperty()
    # values: correct, wrong, unmarked
    result = db.StringProperty()


def save_result(student,question,answer,status,solution = None):
    # find and delete any previous results of same student and same question
    # TODO: maybe I'll keep all results for statistics
    query = StudentResult.all().filter('student =', student).filter('question =', question)
    for res in query.run():
        res.delete()
    
    result = StudentResult()
    result.student = student
    result.question = question
    result.answer = answer
    result.result = status
    if solution:
        result.solution = solution
    result.put()

def get_student_result(student,question):
    """Get result of student answering a question."""
    query = StudentResult.all().filter('student =', student.key()).filter('question =', question)
    if query.count() == 0:
        return None
    # return the best result
    res = None
    for r in query.run():
        if res == None:
            res = r
        rr = r.result
        if rr == 'correct':
            res = r
            break
        elif rr == 'wrong' and res.result != 'correct':
            res = r
    return res

def get_result(student,question):
    """Get result of student answering a question.
    
    Possible values:
    
        'notdone':  no attempt has been made to answer the question,
        'unmarked': question answered but not marked automatically or by the teacher
        'wrong':    question was answered wrong,
        'correct':  question was answered correctly.
    """
    query = StudentResult.all().filter('student =', student.key()).filter('question =', question)
    if query.count() == 0:
        return 'notdone'
    # return the best result
    res = 'unmarked'
    for r in query.run():
        rr = r.result
        if rr == 'correct':
            res = rr
            break
        elif rr == 'wrong' and res != 'correct':
            res = 'wrong'
    return res
