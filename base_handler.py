import webapp2
from webapp2_extras import sessions
from google.appengine.ext import db
from google.appengine.api import users

from myuser import MyUser,create_user,get_user

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    def local_login(self, nickname,password):
        """Log in user without google account.
        
        Args:
            nickname (str): Nickname to login with
            passwd (str): User local password
        
        Return (MyUser):
            Logged in user or None if failed.
        """
        user = get_user(nickname.lower())
        if not user or user.password() != password:
            return None
        self.session['local_user'] = str(user.key())
        return user
        
    def local_logout(self):
        """Log out user without google account."""
        if 'local_user' in self.session:
            del self.session['local_user'];
        
    def get_current_user(self):
        """Return the current user if someone logged in or None otherwise"""
        default_user = 'roman.tolchenov'
        gUser = users.get_current_user()
        if not gUser:
            #return MyUser(key_name=default_user)
            if 'local_user' in self.session:
                user_key = self.session['local_user']
            else:
                return None
            user = MyUser.get(db.Key(encoded=user_key))
        else:
            user = get_user(gUser.nickname().lower())
        if user and not user.user:
            user.user = gUser 
            user.put()
        # if default user logged in but not registered - register him (me)
        if not user and gUser.nickname().lower() == default_user:
            user = MyUser(key_name=default_user)
            user.user = gUser
            user.roles = ['admin','teacher']
            user.put()
        # temporary:
    #    if gUser and gUser.nickname() == default_user:
    #        user.roles = ['admin','teacher']
        return user
    
#    def check_loggedin(func):
#        """Decorator for requests handlers wich must check that a user has logged in"""
#        def check_loggedin_wrapper(self):
#            user = get_current_user()
#            if not user:
#                self.redirect('/')
#                return
#            func(self)
#        return check_loggedin_wrapper
    
    def get_current_admin(self):
        """Return the current user if someone logged in and is an admin or None otherwise"""
        user = self.get_current_user()
        if not user or not user.isAdmin():
            return None
        return user
    
    def get_current_teacher(self):
        """Return the current user if someone logged in and is a teacher or None otherwise"""
        user = self.get_current_user()
        if not user or not user.isTeacher():
            return None
        return user
    
    def get_current_student(self):
        """Return the current user if someone logged in and is a student or None otherwise"""
        user = self.get_current_user()
        if not user or not user.isStudent():
            return None
        return user
    
