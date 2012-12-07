#import cgi
#import datetime
#import urllib
import webapp2

#from google.appengine.ext import db
#from google.appengine.api import users


import myuser

app = webapp2.WSGIApplication([(r'/', myuser.MainPage),
                               (r'/users', myuser.UserList),
                               (r'/deleteuser', myuser.DeleteUser),
                               (r'/adduser', myuser.AddUser),
                               ],
                              debug=True)
