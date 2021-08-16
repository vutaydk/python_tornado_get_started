import tornado.websocket

class EchoWebHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("Websobket opened")
    
    def on_message(self, message):
        self.write_message(u"You said: " + message)
    
    def on_close(self):
        print("Websocket closed")
    
    def check_origin(self, origin: str) -> bool:
        return "localhost" in origin


import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("ws_example.html")


app = tornado.web.Application([
    (r"/", MainHandler),
    (r"/websocket", EchoWebHandler)
])

import tornado.ioloop
if __name__ == "__main__":
    app.listen("8888")
    tornado.ioloop.IOLoop.current().start()