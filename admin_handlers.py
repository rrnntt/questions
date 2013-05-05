import webapp2
from google.appengine.ext import db
from base_handler import BaseHandler
from myuser import MyUser
from mytemplate import write_template

class AdminStartPage(BaseHandler):
    def get(self):
        admin = self.get_current_admin()
        if not admin:
            self.redirect('/')
            return
            
        query = MyUser.all().filter('roles = ', 'teacher')
        teachers = query.fetch(1000)
        template_values = {'teachers':teachers}
        write_template(self, admin, 'admin_start.html', template_values)
        