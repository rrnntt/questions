import webapp2
import myuser
from mytemplate import write_template
#from chapter_module import list_visible_chapters
import chapter_module
import myuser_handlers

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = myuser.get_current_user()
        template_values = {}
        write_template(self, user, 'index.html', template_values)
        
class StudentLogin(webapp2.RequestHandler):
    def get(self):
        write_template(self, None, 'student_login.html', {'in_local_login': True})

app = webapp2.WSGIApplication([(r'/', MainPage),
                               (r'/studentlogin', StudentLogin),
                               (r'/userlist', myuser.UserList),
                               (r'/users', myuser_handlers.MyUsers),
                               (r'/users/(.+)', myuser_handlers.MyUsers),
                               (r'/deleteuser', myuser.DeleteUser),
                               (r'/adduser', myuser.AddUser),
                               (r'/chapterpage', chapter_module.ChapterPage),
                               (r'/chapters', chapter_module.Chapters),
                               (r'/chapters/(.+)', chapter_module.Chapters),
                               ],
                              debug=True)
