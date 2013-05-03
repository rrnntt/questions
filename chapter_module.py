import json
from markdown import markdown

from markdown_postprocess import postprocess
from chapter import *
from myuser import *
from mytemplate import write_template
from question import Question
from image import Image

"""
Chapters are a way of organising questions. A chapter may either include other
chapters or questions.
"""

def set_chapter_text(chapter, text):
    """Parse the new text and correct if needed.
    
    Consider input text to have Markdown format.
    - Image names in reference links need to have urls.
    """
    # find all image tags in form ![Alt text][image_name]
    # and interpret image_name as markdown reference id
    # so text must contain line [image_name]: /proper_image_url
    image_link_pattern = re.compile('!\[.*?\]\[(.+?)\]')
    id_pattern_template = '\[%s\]:.+?'
    match_list = re.findall(image_link_pattern, text)
    refresh = chapter.refresh
    for id in match_list:
        pattern = id_pattern_template % id
        if not re.search(pattern,text):
            image = Image.get_image_by_name(chapter, id)
            if image:
                text += '\n['+id+']: '+'/img?key='+str(image.key())
        elif refresh:
            image = Image.get_image_by_name(chapter, id)
            if image:
                text = re.sub(pattern,'['+id+']: '+'/img?key='+str(image.key()),text)
            else:
                text = re.sub(pattern,'',text)
            
    chapter.text = text
    chapter.refresh = False


###########################################################################
#     Request handlers
###########################################################################
            
class ChapterPage(webapp2.RequestHandler):
    def get(self):
        user = get_current_user()
        if not user:
            self.redirect('/')
            return
        
        encoded_chapter_key = self.request.get('chapter')
        
        chapter, encoded_chapter_key = get_chapter_by_encoded_key(encoded_chapter_key)
        subchapters = list_edit_chapters(user, chapter)
        subchapters_empty = len(subchapters) == 0
        parents = list_parents(chapter)
        parents.reverse()
        
        if chapter.text != None:
            if chapter.refresh:
                text = chapter.text
                set_chapter_text(chapter, text)
                chapter.refresh = False
            chapter_formatted_text = markdown(chapter.text,safe_mode='escape')
            chapter_formatted_text = postprocess(chapter_formatted_text)
        else:
            chapter_formatted_text = ''
            
        questions = list_questions(chapter)
        has_questions = len(questions) > 0
        
        template_values = {
                           'subchapters': subchapters,
                           'subchapters_empty': subchapters_empty,
                           'parents' : parents,
                           'chapter_formatted_text' : chapter_formatted_text,
                           'questions' : questions,
                           'has_questions' : has_questions,
                           }
        
        add_chapter_values(template_values, chapter)
        
        write_template(self, user, 'chapter.html',template_values)
        
class EditChapterPage(webapp2.RequestHandler):
    def get(self):

        user = get_current_user()
        if not user:
            self.redirect('/')
            return
        
        encoded_chapter_key = self.request.get('chapter')
        chapter, encoded_chapter_key = get_chapter_by_encoded_key(encoded_chapter_key)

        questions = list_questions(chapter)
        has_questions = len(questions) > 0
        template_values = {
                           'questions' : questions,
                           'has_questions' : has_questions,
                           }
        add_chapter_values(template_values, chapter)
        template_values['title'] = 'Edit chapter ' + chapter.title
        
        write_template(self, user, 'chapter_edit.html',template_values)
        
###########################################################################
#     Chapters
###########################################################################
class Chapters(webapp2.RequestHandler):
    """Implements REST service for managing chapters"""
    def put(self,Id):
        """Save a chapter with key == Id"""
        #raise Exception(self.request.arguments())
        chapter,ekey = get_chapter_by_encoded_key(Id)
        if chapter:
            jsn = json.decoder.JSONDecoder()
            model = jsn.decode( self.request.get('model'))
            #raise Exception(model[0])
            if not 'parent_key' in model:
                self.response.out.write('error')
                return
            chapter.title = model['title']
            if 'text' in model:
                set_chapter_text(chapter, model['text'])
            chapter.put()
        else:
            raise Exception('Saving of chapter failed')

    def post(self,Id=None):
        """Create new chapter instance and retirn its id which is its key"""
        user = get_current_user()
        if not user:
            self.redirect('/')
            return
            
        #raise Exception(self.request.get('_method'))
        httpMethod = self.request.get('_method')
        if httpMethod == 'PUT':
            self.put(Id)
            return
        if httpMethod == 'DELETE':
            self.delete(Id)
            return
        if httpMethod == 'GET':
            raise Exception('GET not implemented')
            return
            
        jsn = json.decoder.JSONDecoder()
        model = jsn.decode( self.request.get('model'))
        #raise Exception(model[0])
        if not 'parent_key' in model:
            self.response.out.write('error')
        if not 'title' in model:
            self.response.out.write('error')
        
        root = root_key()
        encoded_parent_key = model['parent_key']
        if encoded_parent_key == 'root':
            parent_key = root
        else:
            parent_key = db.Key(encoded=encoded_parent_key)
        
        title = model['title']
            
        if len(title) > 0:
            chapter = Chapter(parent=parent_key)
            chapter.authors.append(user.key())
            chapter.title = title
            chapter.put()
        else:
            self.response.out.write('error')
            return
        
        self.response.out.write('{"id":"'+str(chapter.key())+'"}')

    def delete(self, Id):
        """Delete a chapter with key == Id"""
        chapter,ekey = get_chapter_by_encoded_key(Id)
        if chapter:
            chapter.deleteAll()
        else:
            raise Exception('Deleting of chapter failed')

