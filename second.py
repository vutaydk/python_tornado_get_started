import tornado
from tornado.web import RequestHandler, Application, url


class MainHandler(RequestHandler):
    def __init__(self):
        pass

    def get(self):
        self.write("<a href='%s'></a>" % self.reverse_url("story", "1"))
    

class StoryHandler(RequestHandler):
    def __init__(self, db):
        self.db = db
    def get(self, story_id):
        self.write("this is story %s " % story_id)

class FormHandler(RequestHandler):
    def get(self):
        self.write('<html><body><form action="/myform" method="POST">'
                   '<input type="text" name="message">'
                   '<input type="submit" value="Submit">'
                   '</form></body></html>')
    def post(self):
        self.set_header("Content-Type", "text/plain")
        self.write("You wrote " + self.get_body_argument("message"))

    def prepare(self):
        if self.request.header.get("Content-type", "").startswith("application/json"):
            import json
            self.json_args = json.loads(self.request.body)
        else:
            self.json_args = None

db = {}

app = Application([
    url(r"/", MainHandler),
    url(r"/story/([0-9]+)", StoryHandler, dict(db=db), name="story")
])

