from google.appengine.ext import db
from myuser import MyUser

class Image(db.Model):
    # name of the image that its owner / author refer to it; must be unique
    name = db.StringProperty()
    # binary image data
    data = db.BlobProperty()
    # image type: png, jpeg
    type = db.StringProperty('png')
    
    @classmethod
    def get_my_image_by_name(cls, user, name):
        """Get an image owned by a user by image name"""
        query = Image.all().ancestor(user).filter('name =', name)
        images = query.fetch(10) # there must be at most 1 image but just in case...
        if len(images) == 0:
            return None
        return images[0]
    
