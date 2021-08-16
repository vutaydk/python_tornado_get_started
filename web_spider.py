import time
from datetime import timedelta

from html.parser   import HTMLParser
from urllib.parse import urljoin, urldefrag

from tornado import gen, httpclient, ioloop, queues


base_url = "http://www.tornadoweb.org/en/stable/"
concurrency = 10


async def get_links_from_url(url):
    res = await httpclient.AsyncHTTPClient().fetch(url)
    print(f"Fetched {url}")

    html =res.body.decode(errors="ignore")
    return [urljoin(url, remove_fragment(new_url)) for new_url in get_links(html)]

def remove_fragment(url):
    pure_url, frag = urldefrag(url)
    return pure_url

def get_links(html):
    class URLSeeker(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.urls = []

        def handle_starttag(self, tag, attrs):
            href = dict(attrs).get("href")
            if href and tag == "a":
                self.urls.append(href)
    url_seeker = URLSeeker()
    url_seeker.feed(html)
    return url_seeker.urls


async def main():
    q = queues.Queue()
    start = time.time()
    fetching, fetched, dead = set(), set(), set()

    async def fetch_url(current_url):
        if current_url in fetching:
            return
        
        print(f"Fetching {current_url}")
        fetching.add(current_url)

        urls = await get_links_from_url(current_url)
        fetched.add(current_url)

        for new_url in urls:
            if new_url.startswith(base_url):
                await q.put(new_url)
    
    async def worker():
        async for url in q:
            if not url:
                return
            try:
                await fetch_url(url)
            except Exception as e:
                print(f"Exception: {e} {url}")
                dead.add(url)
            finally:
                q.task_done()
    
    await q.put(base_url)

    workers = gen.multi([worker() for _ in range(concurrency)])
    await q.join(timeout=timedelta(seconds=300))
    assert fetching == (fetched | dead)

    print(f"Done in {time.time() - start} seconds, fetched {len(fetched)}")
    print(f"Unable to fetch {len(dead)} urls")

    for _ in range(concurrency):
        await q.put(None)
    
    await workers

if __name__ == "__main__":
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(main)