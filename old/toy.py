
#!/usr/bin/env python
# ~*~ encoding: utf-8 ~*~


#======
# name: toy.py
# date: 2016JAN03
# prog: pr
# desc: toy implementation of html5lib
# src : <https://github.com/html5lib/html5lib-python>
#       <https://docs.python.org/3.3/library/urllib.request.html#module-urllib.request>
#       <https://github.com/kennethreitz/requests> 
#======


import sys
import bs4
import urllib
import requests
import html5lib

from urllib.request import urlopen
from html5lib import treebuilders
from html5lib import treewalkers
from html5lib import serializer
from html5lib.filters import sanitizer
from html5lib import sanitizer


def eg1(url):
    if url:
        print("url <{}>".format(url))
        with urlopen(url) as f:
            try:
                print(f.getcode())
                print("info={}".format(f.info()))
                #print("opening <{}>".format(dir(f)))
                #document = html5lib(f, encoding=f.info().get_content_charset())
                #print(dir(document))
            except URLError:
                print("error: URL  {}".format(urllib.error.URLError))
            except HTTPError:
                print("error: HTTP {}".format(urllib.error.HTTPError))
            else:
                err = sys.exc_info()[0]
                if err:
                    print("error: {}".format(err))
                else:
                    return True
    else:
        return False

def eg2(url):
    if url:
        print("url <{}>".format(url))
        r = requests.get(url)
        if r:
            print("status={}".format(r.status_code))
            print("headers={}".format(r.headers))
            print("data={}".format(r.text[10]))
            return r.text
        else:
            print("error: failed request")
            return False
    else:
        return False

def pr2(data):
    if data:
        print(">> data={} ({})".format(data[:10], len(data)))
        parser = html5lib.HTMLParser()
        try:
            document = parser.parse(data)
            data = document.items()
            if data:
                for d in data:
                    print(">>> {}".format(d))
        except:
            err = sys.exc_info()[0]
            if err:
                print("error: {}".format(err))

 
    else:
        return False

def pr3(data):
    if data:
        #print("d={}".format(data[10:]))
        element = html5lib.parse(data)
        try:
            #walker = html5lib.getTreeWalker("etree")
            #stream = walker(element)
            #s = html5lib.serializer.HTMLSerializer()
            #output = s.serialize(stream)
            #for item in output:
            #    print("> {}".format(item))
            for e in element:
                for c in e.getchildren():
                    #keys = c.keys()
                    #print("====== K ======")
                    #for k in keys:
                    #    print("key={}".format(k))
                    print("====== V ======")
                    values = c.items()
                    for v in values:
                        print("key={} value={}".format(v[0],v[1]))
                        #print(dir(v))
                        #for item in dir(v):
                        #    print(item)
        except:
            err = sys.exec_info()[0]
            if err:
                print("error: {}".format(err))
    else:
        return False

def pr4(data):
    if data:
        p = html5lib.parse(data)
        walker = html5lib.getTreeWalker('etree')
        s = walker(p)
        stream = html5lib.serializer.HTMLSerializer().serialize(s)
        
        for item in stream:
            print(item, len(item))

        return stream
    else:
        return False

def pr5(data):
    if data:
        
        return True
    else:
        return False

def bs1(data, fk, gk):
    if data:
        s = bs4.BeautifulSoup(data='', "html5lib")
        for img in s.find_all(fk):
            print(img.get(gk))
        return True
    else:
        return False


def main():
    SITES = [{'name':'index',     'url':'http://192.168.1.9'}, 
             {'name':'archive',   'url':'http://192.168.1.9/archives'},
             {'name':'theage',    'url':'http://theage.com.au'},
             {'name':'hn-classic','url':'http://news.ycombinator.com/classic'}]

    for site in SITES:
        print("------ start ------")
        site_name = site['name']
        page_name = "{}.{}".format(site_name, 'html')
        url = site['url']

        print("{}: <{}>".format(site_name, url))
        eg1(url)
        data = eg2(url)
        if data:
            # save to file for use
            with open(page_name, 'w') as f:
                f.write(data)
            f.close()
            bs1(data, fk='img',gk='src')
        else:
            print("error: no data found at <{}>".format(url))
        print("------ end ------\n\n")
if __name__ == "__main__":
    main()


# vim: ff=unix:ts=4:sw=4:tw=78:noai:expandtab
