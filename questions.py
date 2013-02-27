import webapp2
import myuser
from mytemplate import write_template
#from chapter_module import list_visible_chapters
import chapter_module
import myuser_handlers

class MainPage(webapp2.RequestHandler):
    def get(self):

        user = myuser.get_current_user()
        #chapters = list_visible_chapters(user)
        
        #template_values = {'chapters': chapters}
        template_values = {}
        
        write_template(self, user, 'index.html', template_values)

app = webapp2.WSGIApplication([(r'/', MainPage),
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
