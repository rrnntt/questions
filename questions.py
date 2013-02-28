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
        values = {'in_local_login': True,'page': self.request.get('page')}
        write_template(self, None, 'student_login.html', values)

class Login(webapp2.RequestHandler):
    def post(self):
        nickname = self.request.get('nickname')
        password = self.request.get('password')
        page = str(self.request.get('page'))
        user = myuser.local_login(nickname, password)
        if not isinstance(page, str):
            raise Exception('not str!')
        self.redirect(page)

class Logout(webapp2.RequestHandler):
    def get(self):
        myuser.local_logout()
        self.redirect('/')

class TestPage(webapp2.RequestHandler):
    def get(self):
        user = myuser.get_current_user()
        values = {'page': self.request.get('page')}
        write_template(self, user, 'test.html', values)

app = webapp2.WSGIApplication([(r'/', MainPage),
                               (r'/studentlogin', StudentLogin),
                               (r'/login', Login),
                               (r'/logout', Logout),
                               (r'/test', TestPage),
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
