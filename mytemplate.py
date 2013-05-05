import jinja2
import os

from google.appengine.api import users
from course import get_edit_course
from chapter import Chapter

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def write_template(handler, user, file_name, template_values = {}):
    if user:
        if user.user:
            url = users.create_logout_url(handler.request.uri)
        else:
            url = '/logout'
        url_linktext = 'Logout'
        user_name = user.nickname()
    else:
        url = users.create_login_url(handler.request.uri)
        url_linktext = 'Login'
        user_name = ''
        
    # default template values for base.html
    template_values['user'] = user
    template_values['user_name'] = user_name
    template_values['login_url'] = url
    template_values['login_url_text'] = url_linktext
    template_values['local_login_url'] = '/studentlogin?page='+str(handler.request.uri)
    # in_local_login means in student_lgin.html page. This page is different
    # as it shouldn't show neither login nor logout link
    if not 'in_local_login' in template_values:
        template_values['in_local_login'] = 'False'
    if not 'title' in template_values:
        template_values['title'] = 'Questions'
    session = handler.session
    if 'question_list' in session:
        template_values['edit_question_list'] = session['question_list']  
    course = get_edit_course()
    template_values['edit_course'] = course 
    chapter_keys = []
    if course:
        for q in course.chapters:
            chapter = Chapter.get(q)
            if chapter:
                chapter_keys.append(str(chapter.key()))
    template_values['edit_course_chapter_keys'] = chapter_keys
    if 'goto' in template_values:
        goto = template_values['goto']
        if goto == None or goto == '':
            template_values['goto'] = '/'
    
    # write out the template 
    template = jinja_environment.get_template(file_name)
    handler.response.out.write(template.render(template_values))

