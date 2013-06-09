#import logging
#import webapp2
import urllib
from google.appengine.ext import db
#from google.appengine.api import memcache
from image import Image
from base_handler import BaseHandler
from mytemplate import write_template

class ServeImage(BaseHandler):
    def get(self):
        user = self.get_current_user()
        if not user:
            self.error(404)
            return
        key = self.request.get('key')
        if key:
            try:
                image = db.get( key )
            except:
                self.error(404)
                return
        else:
            name = self.request.get('name')
            if not name:
                self.error(404)
                return
            try:
                chapter = db.get( self.request.get('chapter') )
            except:
                self.error(404)
                return
            image = Image.get_image_by_name(chapter, name)
        if not image:
            self.error(404)
            return
        
        thumbnail = self.request.get('thumbnail')
        serveThumbnail = thumbnail and thumbnail == 'true'
            
        self.response.headers['Content-Type'] = str('image/'+image.type)
        if serveThumbnail:
            self.response.out.write(image.icon)
        else:
            self.response.out.write(image.data)

class UploadImage(BaseHandler):
    def post(self):
        user = self.get_current_user()
        if not user:
            self.redirect('/')
            return
        name = self.request.get('name')
        overwrite = self.request.get('overwrite')
        chapter = db.get( self.request.get('chapter') )
        args = { 'chapter': chapter.key() }
        if len(name) == 0:
            args['error'] = 'Image must have a name.'
        else:
            old_image = Image.get_image_by_name(chapter, name)
            if overwrite.lower() == 'true':
                if old_image:
                    old_image.delete()
                    chapter.refresh = True
                    chapter.put()
                old_image = None
            if old_image:
                args['image'] = old_image.key()
                args['error'] = 'Image with this name already exists.'
            else:
                data = self.request.get('img')
                if len(data) == 0:
                    args['error'] = 'No data received.' 
                else:
                    image = Image.create(chapter, name, data)
                    args['image'] = image.key()
                    chapter.refresh = True
        self.redirect('/uploadimagepage?%s' % urllib.urlencode(args))
        
class UploadImagePage(BaseHandler):
    def get(self):
        user = self.get_current_user()
        if not user:
            self.redirect('/')
            return
        #raise Exception('chapter '+self.request.get('chapter'))
        chapter = db.get( self.request.get('chapter') )
        key = self.request.get('image')
        if key:
            image = db.get( key )
        else:
            image = None
        error = self.request.get('error')
        if error == '':
            error = None
        
        template_values = {'image':image, 
                           'error': error,
                           'chapter': chapter,
                           }
        write_template(self, user, 'image_upload.html', template_values)
        
class ImageListPage(BaseHandler):
    def get(self):
        user = self.get_current_user()
        if not user:
            self.redirect('/')
            return
        
        chapter = db.get( self.request.get('chapter') )
            
        query = db.Query(Image).filter('chapter =',chapter)
        images = query.fetch(1000)
        not_empty = len(images) > 0

        template_values = {'images': images,
                           'not_empty': not_empty,
                           'chapter': chapter,
                           }
        write_template(self, user, 'image_list.html', template_values)
        
class ImagePage(BaseHandler):
    def get(self):
        user = self.get_current_user()
        if not user:
            self.redirect('/')
            return
        
        chapter = db.get( self.request.get('chapter') )
        try:
            image = db.get( self.request.get('image') )
        except:
            self.redirect('/imagelistpage?%s' % urllib.urlencode({'chapter': chapter.key()}))
            return
            
        template_values = {'image': image,
                           'chapter': chapter,
                           }
        write_template(self, user, 'image.html', template_values)
