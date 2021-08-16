import mimetypes

import tornado
from tornado import gen

@gen.coroutine
def multipart_producer(boundary, filenames, write):
    boundary_bytes = boundary.encode()
    for filename in filenames:
        filename_bytes = filename.encode()
        mtype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        buf = (
            (b"--%s\r\n" % boundary_bytes)
            + (
                b'Content-Disposition: form-data; name="%s"; filename="%s"\r\n'
                % (filename_bytes, filename_bytes)
            )
            + (b"Content-Type: %s\r\n" % mtype.encode())
            + b"\r\n"
        )

        yield write(buf)

        with open(filename, "rb") as f:
            while True:
                chunk = f.read(16*1024)
                if not chunk:
                    break
                yield write(chunk)
        
        yield write(b"\r\n")
    yield write(b"--%s--\r\n" % (boundary_bytes,))

from tornado import httpclient
from uuid import uuid4
from functools import partial

async def post(filenames):
    client = httpclient.AsyncHTTPClient()
    boundary = uuid4().hex
    header = {"Content-Type": "multipart/form-data; boundary=%s" % boundary}
    producer = partial(multipart_producer, boundary, filenames)
    response = await client.fetch(
        "http://localhost:8888/post",
        method="POST", 
        headers=header, 
        body_producer= producer)
    
    print(response)

async def raw_producer(filename, write):
    with open(filename, "rb") as f:
        while True: 
            chunk = f.read(16*1024)
            if not chunk: 
                break

            yield chunk

from urllib.parse import quote
import os

async def put(filenames):
    client = httpclient.AsyncHTTPClient()
    for filename in filenames:
        mtype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        headers = {"Content-Type": mtype}
        producer = partial(raw_producer, filename)
        url_path = quote(os.path.basename(filename))
        response = await client.fetch(
            "http://localhost:8888/%s" % url_path,
            method="PUT",
            headers=headers,
            body_producer=producer
        )
        print(response)
    
from tornado.options import define, options
from tornado import ioloop
import sys
if __name__ == "__main__":
    define("put", type=bool, help="Use PUT instead of POST", group="file uploader")

    filenames = options.parse_command_line()
    if not filenames:
        print("Provide a list of filename to upload.", file=sys.strerr)
        sys.exit(1)
    
    method = put if options.put else post
    ioloop.IOLoop.current().run_sync(lambda: method(filenames))
