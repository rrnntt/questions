#import cgi
#import datetime
#import urllib
import webapp2

#from google.appengine.ext import db
#from google.appengine.api import users


import myuser
from mytemplate import write_template
from chapter_module import list_visible_chapters
import chapter_module

class MainPage(webapp2.RequestHandler):
    def get(self):

        user = myuser.get_current_user()
        chapters = list_visible_chapters(user)
        
        template_values = {'chapters': chapters}
        
        write_template(self, user, 'index.html', template_values)

app = webapp2.WSGIApplication([(r'/', MainPage),
                               (r'/users', myuser.UserList),
                               (r'/deleteuser', myuser.DeleteUser),
                               (r'/adduser', myuser.AddUser),
                               (r'/addchapterpage', chapter_module.AddChapterPage),
                               (r'/addchapter', chapter_module.AddChapter),
                               (r'/chapterpage', chapter_module.ChapterPage),
                               ],
                              debug=True)
