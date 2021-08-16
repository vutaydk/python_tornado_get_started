import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid

from tornado.options import options, define
define("port", default=8888, help="default port")

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", messages=ChatSocketHandler.cache)

class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 20

    def open(self):
        ChatSocketHandler.waiters.add(self)
    
    def on_close(self):
        ChatSocketHandler.waiters.remove(self)

    def get_compression_options(self):
        return {}    
    
    @classmethod
    def save_msg(cls, chat):
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[1:]

    @classmethod
    def broadcast_msg(cls, chat):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error when sending msg")
    
    def on_message(self, message):
        logging.info("got new message: %r", message)
        parsed_msg = tornado.escape.json_decode(message)
        chat = {"id": str(uuid.uuid4()), "body": parsed_msg["body"]}
        chat["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=chat)
        )

        ChatSocketHandler.save_msg(chat)
        ChatSocketHandler.broadcast_msg(chat)

def main():
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/chatsocket", ChatSocketHandler)
        ],
       
        cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=True,
        )
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()