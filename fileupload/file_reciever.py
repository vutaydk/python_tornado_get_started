import tornado.web
import logging


class PostHandler(tornado.web.RequestHandler):
    def post(self):
        for field_name, files in self.request.files.items():
            for info in files:
                filename, content_type = info["filename"], info["content_type"]
                body = info["body"]
                logging.info(f"POST {filename} {content_type} {len(body)} bytes")   
        
        self.write("OK")

from urllib.parse import unquote

@tornado.web.stream_request_body
class PutHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.bytes_read = 0
    
    def data_received(self, chunk):
        self.bytes_read += len(chunk)
    
    def put(self, filename):
        filename = unquote(filename)
        mtype = self.request.headers.get("Content-Type")
        logging.info(f" PUT {filename} {mtype} {self.bytes_read} bytes")
        self.write("OK")

def make_app():
    return tornado.web.Application([
        (r"/post", PostHandler),
        (r"/(.*)", PutHandler)
    ])

from tornado import options
from tornado import ioloop

if __name__ == "__main__":
    options.parse_command_line()
    app = make_app()
    app.listen(8888)
    ioloop.IOLoop.current().start()