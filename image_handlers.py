import webapp2
import urllib
from google.appengine.ext import db
from google.appengine.api import memcache
from image import Image
from myuser import get_current_user
from mytemplate import write_template

def start_pagination():
    memcache.delete('imagelistpage')
    memcache.delete('imagelistpage_npages')

class ServeImage(webapp2.RequestHandler):
    def get(self):
        key = self.request.get('key')
        if key:
            image = db.get( key )
        else:
            name = self.request.get('name')
            if not name:
                self.error(404)
                return
            user = get_current_user()
            if not user:
                self.error(404)
                return
            image = Image.get_my_image_by_name(user, name)
            
        self.response.headers['Content-Type'] = str('image/'+image.type)
        self.response.out.write(image.data)

class UploadImage(webapp2.RequestHandler):
    def post(self):
        user = get_current_user()
        if not user:
            self.redirect('/')
            return
        name = self.request.get('name')
        if len(name) == 0:
            args = { 'error': 'Image must have a name.' }
        else:
            old_image = Image.get_my_image_by_name(user, name)
            if old_image:
                args = { 'key': old_image.key(), 'error': 'Image with this name already exists.' }
            else:
                data = self.request.get('img')
                if len(data) == 0:
                    args = { 'error': 'No data received.' }
                else:
                    image = Image(parent=user)
                    image.name = name
                    image.data = db.Blob(data)
                    image.type = 'png'
                    image.put()
                    start_pagination()
                    args = { 'key': image.key() }
        self.redirect('/uploadimagepage?%s' % urllib.urlencode(args))
#        self.redirect('/?' + urllib.urlencode(
#            {'guestbook_name': guestbook_name}))
        
class UploadImagePage(webapp2.RequestHandler):
    def get(self):
        user = get_current_user()
        if not user:
            self.redirect('/')
            return
        key = self.request.get('key')
        if key:
            image = db.get( key )
        else:
            image = None
        error = self.request.get('error')
        if error == '':
            error = None
        write_template(self, user, 'image_upload.html', {'image':image, 'error': error})
        
class ImageListPage(webapp2.RequestHandler):
    def get(self):
        user = get_current_user()
        if not user:
            self.redirect('/')
            return
        
#        start_pagination()
        # number of images per page
        npp = 1000
#        n_pages = memcache.get('imagelistpage_npages')
#        if n_pages == None:
#            n = db.Query(Image).ancestor(user).count()
#            n_pages = n // npp
#            if n_pages * npp != n:
#                n_pages += 1
#            memcache.add('imagelistpage_npages', n_pages)
#        
#        index = self.request.get('page')
#        if not index:
#            index = 0
#        else:
#            index = int(index)
#            
#        if index < 0:
#            index = 0
#            
#        if index >= n_pages:
#            index = n_pages - 1
#            
#        cursor_list = memcache.get('imagelistpage')
#            
#        if not cursor_list:
#            cursor_list = [None]
#            memcache.add('imagelistpage',cursor_list)
#            
#        n_past_pages = len(cursor_list)
#        if index < n_past_pages:
#            page = cursor_list[index]
#        elif index == 0:
#            page = None
#        else:
#            i = n_past_pages
#            page = cursor_list[-1]
#            while i < index:
#                query = db.Query(Image, cursor=page, keys_only=True).ancestor(user)
#                keys = query.fetch(npp)
#                page = query.cursor()
#                cursor_list.append(page)
#                i += 1
#            memcache.set('imagelistpage', cursor_list)
#            n_past_pages = len(cursor_list)  
            
        query = db.Query(Image).ancestor(user)
        images = query.fetch(npp)
#        next_page = query.cursor()
#        
#        if index == n_past_pages - 1:
#            cursor_list.append(next_page)
#        memcache.set('imagelistpage',cursor_list)
        
        not_empty = len(images) > 0

        template_values = {'images': images,
                           'not_empty': not_empty,
#                           'index': index,
#                           'npages': n_pages,
#                           'cl': cursor_list,
                           }
        write_template(self, user, 'image_list.html', template_values)
