import tornado.web
import tornado

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class MainHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
            return
        
        name = self.get_current_user()
        self.write(name)
    
class LoginHandler(BaseHandler):
    def get(self):
        self.write('<html><body><form action="/login" method="post">'
                   'Name: <input type="text" name="name">'
                   '<input type="submit" value="Sign in">'
                   '</form></body></html>')
    
    def post(self):
        self.set_secure_cookie("user", self.get_argument("name"))
        self.redirect("/")
    
app = tornado.web.Application([
    (r"/", MainHandler),
    (r"/login", LoginHandler)
], cookie_secret="afdafdafdafda")


from tornado import ioloop

if __name__ == "__main__":
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()