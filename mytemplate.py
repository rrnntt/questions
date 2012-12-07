import jinja2
import os

from google.appengine.api import users

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def write_template(handler, user, file_name, template_values = {}):
    if user:
        url = users.create_logout_url(handler.request.uri)
        url_linktext = 'Logout'
        user_name = user.nickname()
    else:
        url = users.create_login_url(handler.request.uri)
        url_linktext = 'Login'
        user_name = ''
    template_values['user'] = user
    template_values['user_name'] = user_name
    template_values['login_url'] = url
    template_values['login_url_text'] = url_linktext
    template = jinja_environment.get_template(file_name)
    handler.response.out.write(template.render(template_values))

