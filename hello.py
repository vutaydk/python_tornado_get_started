# from tornado import httpclient
# import tornado.ioloop
# import tornado.web

# class MainHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.write("Hello world")
    
# def make_app():
#     return tornado.web.Application([
#         (r'/', MainHandler)
#     ])

# if __name__ == "__main__":
#     app = make_app()
#     app.listen(8888)
#     tornado.ioloop.IOLoop.current().start()



# from tornado.httpclient import HTTPClient, AsyncHTTPClient

# def sync_fetch(url):
#     client = HTTPClient()
#     res = client.fetch(url)
#     return res.boy

# async def async_fetch(url):
#     client = AsyncHTTPClient()
#     res = await client.fetch(url)
#     return res.body

