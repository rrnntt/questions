import webapp2
import myuser
from mytemplate import write_template
#from chapter_module import list_visible_chapters
import chapter_module
import myuser_handlers
import admin_handlers
import teacher_handlers
import aclass_handlers
import question_handlers
import question_list_handlers
import course_handlers

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = myuser.get_current_user()
        template_values = {}
        if user:
            if user.isAdmin():
                self.redirect('/adminstart')
                return
            elif user.isTeacher():
                self.redirect('/teacherstart')
                return
            else:
                write_template(self, user, 'index.html', template_values)
        else:
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

class StartPage(webapp2.RequestHandler):
    def get(self):
        user = myuser.get_current_user()
        values = {'page': self.request.get('page')}
        write_template(self, user, 'test.html', values)

app = webapp2.WSGIApplication([(r'/', MainPage),
                               (r'/studentlogin', StudentLogin),
                               (r'/login', Login),
                               (r'/logout', Logout),
                               (r'/test', TestPage),
                               
                               (r'/adminstart', admin_handlers.AdminStartPage),
                               
                               (r'/teacherstart', teacher_handlers.StartPage),
                               (r'/teacherclass', teacher_handlers.ClassPage),
                               
                               (r'/classes', aclass_handlers.Classes),
                               (r'/classes/(.+)', aclass_handlers.Classes),
                               (r'/students', aclass_handlers.Students),
                               (r'/students/(.+)', aclass_handlers.Students),
                               
                               (r'/userlist', myuser_handlers.UserList),
                               (r'/users', myuser_handlers.MyUsers),
                               (r'/users/(.+)', myuser_handlers.MyUsers),
                               (r'/deleteuser', myuser_handlers.DeleteUser),
                               (r'/adduser', myuser_handlers.AddUser),
                               
                               (r'/chapterpage', chapter_module.ChapterPage),
                               (r'/chaptereditpage', chapter_module.EditChapterPage),
                               (r'/chapters', chapter_module.Chapters),
                               (r'/chapters/(.+)', chapter_module.Chapters),
                               (r'/questions', question_handlers.Questions),
                               (r'/questions/(.+)', question_handlers.Questions),
                               (r'/questioneditpage', question_handlers.EditQuestionPage),
                               
                               (r'/questionlist', question_list_handlers.QuestionListRESTHandler),
                               (r'/questionlist/(.+)', question_list_handlers.QuestionListRESTHandler),
                               (r'/questionlistpage', question_list_handlers.QuestionListPage),
                               (r'/savequestionlist', question_list_handlers.SaveQuestionList),
                               (r'/createquestionlist', question_list_handlers.CreateQuestionList),
                               (r'/cancelquestionlist', question_list_handlers.CancelEditQuestionList),
                               
                               (r'/course', course_handlers.CourseRESTHandler),
                               (r'/course/(.+)', course_handlers.CourseRESTHandler),
                               (r'/coursepage', course_handlers.CoursePage),
                               (r'/savecourse', course_handlers.SaveCourse),
                               (r'/createcourse', course_handlers.CreateCourse),
                               (r'/cancelcourse', course_handlers.CancelEditCourse),
                               ],
                              debug=True)
