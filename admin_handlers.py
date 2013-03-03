import webapp2
from google.appengine.ext import db
from myuser import MyUser,create_user,get_current_admin
from mytemplate import write_template

class AdminStartPage(webapp2.RequestHandler):
    def get(self):
        admin = get_current_admin()
        if not admin:
            self.redirect('/')
            return
            
        query = MyUser.all().filter('roles = ', 'teacher')
        teachers = query.fetch(1000)
        template_values = {'teachers':teachers}
        write_template(self, admin, 'admin_start.html', template_values)
        