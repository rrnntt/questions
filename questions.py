import webapp2
import json
from google.appengine.api import users

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
import student_handlers
import image_handlers
from base_handler import BaseHandler

class MainPage(BaseHandler):
    def get(self):
        user = self.get_current_user()
        template_values = {}
        if user:
            if user.isAdmin():
                self.redirect('/adminstart')
                return
            elif user.isTeacher():
                self.redirect('/teacherstart')
                return
            elif user.isStudent():
                self.redirect('/studentstart')
                return
            else:
                write_template(self, user, 'index.html', template_values)
        else:
            write_template(self, user, 'index.html', template_values)
        
class StudentLogin(BaseHandler):
    def get(self):
        values = {'in_local_login': True,'page': self.request.get('page')}
        write_template(self, None, 'student_login.html', values)

class Login(BaseHandler):
    def post(self):
        nickname = self.request.get('nickname')
        password = self.request.get('password')
        page = str(self.request.get('page'))
        user = self.local_login(nickname, password)
        if not isinstance(page, str):
            raise Exception('not str!')
        self.redirect(page)

class Logout(BaseHandler):
    def get(self):
        user = self.get_current_user()
        if user:
            if user.isLocal():
                self.local_logout()
            else:
                url = users.create_logout_url(self.request.uri)
                self.redirect(url)
                return
        self.redirect('/')

class StartPage(BaseHandler):
    def get(self):
        user = self.get_current_user()
        values = {'page': self.request.get('page')}
        write_template(self, user, 'test.html', values)
        
class GetUniqueName(BaseHandler):
    def get(self):
        res = {}
        res['nickname'] = myuser.get_unique_nickname()
        res['password'] = myuser.get_random_password()
        self.response.out.write(json.dumps(res))
        
        
config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}

app = webapp2.WSGIApplication([(r'/', MainPage),
                               (r'/studentlogin', StudentLogin),
                               (r'/login', Login),
                               (r'/logout', Logout),
                               (r'/getuniquename', GetUniqueName),
                               
                               (r'/img', image_handlers.ServeImage),
                               (r'/imagelistpage', image_handlers.ImageListPage),
                               (r'/imagepage', image_handlers.ImagePage),
                               (r'/uploadimage', image_handlers.UploadImage),
                               (r'/uploadimagepage', image_handlers.UploadImagePage),
                               
                               (r'/adminstart', admin_handlers.AdminStartPage),
                               
                               (r'/teacherstart', teacher_handlers.StartPage),
                               (r'/teacherclass', teacher_handlers.ClassPage),
                               (r'/teacherclassedit', teacher_handlers.EditClassPage),
                               
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
                               (r'/answer/(.+)', question_handlers.Answer),
                               
                               (r'/questionlist', question_list_handlers.QuestionListRESTHandler),
                               (r'/questionlist/(.+)', question_list_handlers.QuestionListRESTHandler),
                               (r'/questionlistpage', question_list_handlers.QuestionListPage),
                               (r'/savequestionlist', question_list_handlers.SaveQuestionList),
                               (r'/createquestionlist', question_list_handlers.CreateQuestionList),
                               (r'/cancelquestionlist', question_list_handlers.CancelEditQuestionList),
                               (r'/deletequestionlist', question_list_handlers.DeleteEditQuestionList),
                               
                               (r'/course', course_handlers.CourseRESTHandler),
                               (r'/course/(.+)', course_handlers.CourseRESTHandler),
                               (r'/coursepage', course_handlers.CoursePage),
                               (r'/savecourse', course_handlers.SaveCourse),
                               (r'/createcourse', course_handlers.CreateCourse),
                               (r'/cancelcourse', course_handlers.CancelEditCourse),
                               (r'/deletecourse', course_handlers.DeleteEditCourse),
                               
                               (r'/studentstart', student_handlers.StartPage),
                               (r'/studentchapterpage', student_handlers.ChapterPage),
                               (r'/studentselectclass', student_handlers.SelectClass),
                               (r'/studentcoursespage', student_handlers.CoursesPage),
                               (r'/studentcoursepage', student_handlers.CoursePage),
                               ],
                              debug=True, config=config)
