#!/usr/bin/env python
# ~*~ encoding: utf-8 ~*~


#======
# name: wtm.py
# date: 2016JAN08
# prog: pr
# desc: find the combined weight of a web page or site
#
# src : <https://github.com/html5lib/html5lib-python>
#       <https://docs.python.org/3.3/library/urllib.request.html#module-urllib.r
#       <https://github.com/kennethreitz/requests>
#       <http://www.crummy.com/software/BeautifulSoup/>
#       <http://www.crummy.com/software/BeautifulSoup/bs4/doc/>
#       <http://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python>
#       <https://docs.python.org/3.2/library/urllib.parse.html>
#======


import sys


import bs4
import requests
import html5lib
import validators
import urllib.parse


class Page(object):
    def __init__(self, objreq=requests, 
                       objbs4=bs4, 
                       objval=validators,
                       objpar=urllib.parse):
        self.objreq = objreq
        self.objbs = objbs4
        self.objval = objval
        self.objpar = objpar

        self.base_url = ""
        self.head_name = ['content-type',
                          'status_code',
                          'encoding',
                          'last-modified',
                          'date',
                          'content-length']
        self.headers = {}
        self.urls = []     # url = {'value': 0, 'key':'', 'header':{}}
        self.counter = 0
    def request(self, url):
        print("reading <{}>".format(url))
        if url:
            
            # urllib.parse.urlparse returns tuple, 
            # index 1 == netloc/network locatino part as str
            #bu = self.objpar.urlparse(url)
            #if bu:
            #    self.base_url = bu[1]  #self.objpar.netloc
            #bu = None

            r = self.objreq.get(url)
            self.data = r.text
            self.headers = r.request
            self.add_url(value=url, key='root')
            r = None
            return True
        else:
            return False
    def query(self):
        """query existing page for urls"""
        if self.counter > 0:
            print("querying...")
            for url in self.urls:
                k = url['key']
                v = url['value']

                # ------ fix broken same site urls ------
                # problem: 
                if self.is_valid_url(v):
                    status = self.request(v)
                    print("\t{} q {} <{}>".format(status, k, v))
                else:
                    print("\tinvalid <{}>".format(url))
                    path = v # path is the value of the url
                    
                    #fix_url = "{}/{}".format(self.base_url, path)
                    # urllib.parse.urljoin 
                    fix_url = self.objpar.urljoin(self.base_url, path)
                    status = self.request(fix_url)

                    print("\tbase url: <{}>".format(self.base_url))
                    print("\tbad path: <{}>".format(path))
                    print("\tnew url: <{}>".format(fix_url))
                    print("\tfix url: '{}' is <{}> status [{}]".format(k, fix_url, status))
            return True
        else:
            return False
    def process(self):
        self.get_image()
        self.get_css()
        return True
    def is_valid_url(self, url):
        """check valid url"""
        if url:
            print("is valid? <{}>".format(url))
            if self.objval.url(url):
                return True
            else:
                return False
        else:
            return False
    def add_url(self, value, key):
        """create list of urls to investigate"""
        if value:
            self.urls.append({'value': value, 'key':key})
            return True
        else:
            return False
    def get_urls(self):
        """return list of url dictionary"""
        return self.urls
    def get(self, key1, key2, name):
        """
        find items from page with key1 (optional key2 from item) 
        using name as identifier in url list.
        """
        found = self.objbs.BeautifulSoup(self.data, "html5lib")
        for item in found.find_all(key1):
            if item:
                if key2:
                    found = item.get(key2)
                else:
                    found = item
                self.add_url(value=found, key=name)
            else:
                pass
        return True
    def get_image(self):
        """extract all image data from page"""
        print("\timages")
        return self.get('img', 'src', 'img')
    def get_css(self):
        """extract css data from page"""
        print("\tcss")
        return self.get('link','href','css')
    def count(self):
        """count resources from page"""
        i = 0
        for item in self.get_urls():
            i = i + 1
        self.counter = i
        return self.counter

def main():
    p = Page()
    p.base_url = "http://192.168.1.9/"
    p.request('http://192.168.1.9/archives')
    p.process() 
    urls = p.get_urls()
    count = p.count()
    print(count)
    p.query()

    for u in p.urls:
        print(u)

if __name__ == "__main__":
    main()


# vim: ff=unix:ts=4:sw=4:tw=78:noai:expandtab
