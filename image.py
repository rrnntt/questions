from google.appengine.ext import db
from google.appengine.api import images
from chapter import Chapter

class Image(db.Model):
    # chapter containing this image
    chapter = db.ReferenceProperty(Chapter)
    # name of the image that its owner / author refer to it; must be unique
    name = db.StringProperty()
    # image type: png, jpeg
    type = db.StringProperty('png')
    # binary image data
    data = db.BlobProperty()
    # thumbnail view of the image
    icon = db.BlobProperty()
    
    @classmethod
    def create(cls, chapter, name, data):
        """Create a new instance of Image"""
        image = Image()
        image.chapter = chapter
        image.name = name
        image.data = db.Blob(data)
        img = images.Image(image.data)
        img.resize(64, 64)
        image.icon = img.execute_transforms()
        image.type = 'png'
        image.put()
        return image
    
    @classmethod
    def get_image_by_name(cls, chapter, name):
        """Get an image by its name"""
        query = Image.all().filter('chapter =',chapter).filter('name =', name)
        images = query.fetch(10) # there must be at most 1 image but just in case...
        if len(images) == 0:
            # try parents
            parent = chapter.parent()
            if parent:
                img = cls.get_image_by_name(parent,name)
                return img
            return None
        return images[0]
    
