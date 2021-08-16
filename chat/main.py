import asyncio
import tornado.locks
from tornado.options import options, define, parse_command_line

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")

class MessageBuffer:
    def __init__(self):
        self.cond = tornado.locks.Condition()
        self.cache = []
        self.cache_size = 20
    
    def get_messages_since(self, cursor):
        results = []
        for msg in reversed(self.cache):
            if msg["id"] == cursor:
                break
            results.append(msg)
        results.reverse()
        return results
    
    def add_message(self, msg):
        self.cache.append(msg)
        if len(self.cache) > self.cache_size:
            self.cache = self.cache[1:]
        self.cond.notify_all()


global_message_buffer = MessageBuffer()


import tornado.web
import tornado.escape
from uuid import uuid4


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", messages = global_message_buffer.cache)

class MessageNewHandler(tornado.web.RequestHandler):
    def post(self):
        message = {
            "id": str(uuid4()),
            "body": self.get_argument("body")
        }

        message["html"] = tornado.escape.to_unicode(
            self.render_string("message.html", message=message)
        )

        if self.get_argument("next", None):
            self.redirect(self.get_argument("next"))
        else:
            self.write(message)
        
        global_message_buffer.add_message(message)

class MessageUpdateHandler(tornado.web.RequestHandler):
    """Long-pooling, wait until new message come before return

    Args:
        tornado ([type]): [description]
    """

    async def post(self):
        cursor = self.get_argument("cursor", None)
        messages = global_message_buffer.get_messages_since(cursor)
        while not messages:
            self.wait_future = global_message_buffer.cond.wait()
            try:
                await self.wait_future
            except asyncio.CancelledError:
                return
            messages = global_message_buffer.get_messages_since(cursor)
        
        if self.request.connection.stream.closed():
            return
        
        self.write(dict(messages=messages))
    
    def on_connection_close(self):
        self.wait_future.cancel()


import os
import tornado.ioloop

def main():
    parse_command_line()
    app = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/a/message/new", MessageNewHandler), 
            (r"/a/message/updates", MessageUpdateHandler)
        ],
        cookie_secret = "aaaaaaaaaaa",
        template_path = os.path.join(os.path.dirname(__file__), "templates"),
        static_path = os.path.join(os.path.dirname(__file__), "statics"),
        xsrf_cookies = True,
        debug = options.debug
    )

    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()