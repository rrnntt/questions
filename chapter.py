import webapp2
from google.appengine.ext import db

class Chapter(db.Model):
    title = db.StringProperty()

