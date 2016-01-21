#!/usr/bin/env python
# ~*~ encoding: utf-8 ~*~


#======
# name: measure.py
# date: 2016JAN08
# prog: pr
# desc: find the combined weight of a web page or site
#
# src : <https://github.com/html5lib/html5lib-python>
#       <https://docs.python.org/3.3/library/urllib.request.html#module-urllib.r
#       <https://github.com/kennethreitz/requests>
#       <http://www.crummy.com/software/BeautifulSoup/>
#       <http://www.crummy.com/software/BeautifulSoup/bs4/doc/>
#       <http://stackoverflow.com/questions/328356/extracting-text-from-html-file-us
#       <https://docs.python.org/3.2/library/urllib.parse.html>
#======

import os
import sys


import bs4
import requests
import html5lib
import validators
import urllib.parse

from tools import Display

#======
# name: Page
# date: 2016JAN10
# prog: pr
# desc: given a url, measure that page
# src : 
# todo: * itterate urls, save at root
#       - don't save text
#       * JSON-ify the storeage 
#       * don't record text OR store seperatly
#======
class Page(object):
    def __init__(self, 
                 objval=validators,
                 objreq=requests,
                 objurl=urllib.parse,
                 objbs=bs4,
                 objdis=display):
        #------ objects ------
        self.objval = objval      # valid url test
        self.objreq = objreq      # http requests
        self.objurl = objurl      # url tools 
        self.objbs  = objbs       # extract from page
        self.objrequest = None    # internal use of request obj
        self.objdis = objdis
        #------ data ------
        self.length = 0
        self.data = []
        self.urls = []
        self.resources = []
        self.measurement = {'name': '',
                            'url': '',
                            'resource': [],
                            'header': {},
                            'type': '',
                            'text': '',
                            'size': 0}
        #------ data end ------
    def request(self, url):
        """first pass of url, download and extract header"""
        if self.is_valid_url(url):
            self.objdis.msg("request\n\t<{}>".format(url))
 
            self.objrequest = self.objreq.get(url)
            header = self.objrequest.headers
            text = self.objrequest.text



            self.measurement['header'] = header
            self.measurement['url'] = url
            self.measurement['name'] = self.url2name(url)
            self.measurement['type'] = "site"
            self.data.append(self.measurement)
            self.measurement = {'name': '',
                            'url': '',
                            'resource': [],
                            'header': {},
                            'type': '',
                            'text': '',
                            'size': 0}

            return True
        else:
            return False
    def process(self, url):
        if self.request(url):
            self.objdis.msg("process\n\t<{}>".format(url))

            name = self.url2name(url)
            text = self.objrequest.text
            header = self.objrequest.headers

            #------ extract from text ------
            self.get_img(text)
            #self.get_css(text)
            #self.get_js(text)
            #self.get_meta(text)
            #------ end extract ------

            self.request_resources()

            self.measurement['resource'] = self.resources
            self.save(name, self.measurement)

            self.clear()
            self.objrequest = None
            return True
        else:
            return False
    def request_resources(self):
        """
        request from list of resource urls collected
        query them and append to data collected. 
        """
        # do we have any to process?
        number = len(self.urls)
        if number > 0:
            for item in self.urls:
                url = item['value']
                url_type = item['value']
 
                self.objdis.msg("request resource\n\t<{}>".format(url))


                # not sure what to do here
                # fix URL
                if not self.is_valid_url(url):
                    #path = url
                    #url = self.objurl.urljoin(self.base_url, path)
                    self.objdis.warn("request_resources")
                    self.objdis.warn("\trepaired url <{}>".format(url))
                    break

                r = self.objreq.get(url)
                header = r.headers
                text = r.text
 
                if not self.store(text, header, url):
                    self.objdis.warn("request_resources")
                    self.objdis.warn("\turl    <{}>".format(url))
                    self.objdis.warn("\theader {}".format(header))
                r = None
               
            return True 
        else:
            self.objdis.warn("request_resources")
            self.objdis.warn("\turl No is zero")
            return False
    #------ guts start ------
    #   get 
    def get_img(self, data):
        self.get(data, 'img', 'src', 'img')
        self.get(data, 'link', 'href', 'png')
        return True
    def get_css(self, data):
        return self.get(data, 'link', 'href', 'css')
    def get_js(self, data):
        return self.get(data, 'link', 'href', 'js')
    def get_meta(self, data):
        self.get(data, 'meta', 'content', 'png')
    def add_url(self, key, value):
        self.objdis.msg2("add_url")
        if value:
            vn = len(value)
        else:
            vn = "''"
        self.objdis.msg2("k={} v={}".format(key, vn))
        if value:
            self.urls.append({'value': value, 'key': key})
            return True
        else:
            self.objdis.warn("addurl(value={},key={}".format(value, key))
            return False
    def get(self, data, key1, key2, name):
        self.objdis.msg("get ({})".format(name))
        self.objdis.msg2("mame {}: k1={} k2={}".format(name, key1, key2))
        found = self.objbs.BeautifulSoup(data, "html5lib")
        for item in found.find_all(key1):
            if item:
                if key2:
                    found = item.get(key2)
                else:
                    found = item
                if self.add_url(value=found, key=name):
                    pass
                else:
                    self.objdis.warn("add_url error".format(found, name))
                    self.objdis.warn("\tvalue <{}>".format(found))
                    self.objdis.warn("\tkey   <{}>".format(name))
            else:
                pass
        return True
    def store(self, text, header, url, save=True):
        """capture data and store it in resources list"""
        size = 0
        if 'content-length' in header:
            size = header['content-length']
        elif:
            size = len(text)
        else: size = 0

        self.measurement['header'] = header
        self.measurement['size'] = size
        self.measurement['url'] = url
        self.measurement['name'] = self.url2name(url)
        self.measurement['type'] = "resource"
        
        self.resources.append(self.measurement)

        self.measurement = {'name': '',
                            'url': '',
                            'resource': [],
                            'header': {},
                            'type': '',
                            'text': '',
                            'size': 0}
        return True
    def clear(self):
        self.length = 0
        self.urls = []
        self.data = []
        self.measurement = {'name': '',
                            'url': '',
                            'resource':[],
                            'header': {},
                            'type': '',
                            'text': '',
                            'size': 0}
    def save(self, name, measurement):
        """save measurement by name to file"""
        self.objdis.msg("save {}".format(name))

        # save as text now, try json later
        fn = "{}.txt".format(name)

        # save to dir relative to exdir in 'DAT'
        fpn = os.path.join(os.getcwd(),'dat/', fn)
        m = "{}".format(measurement)
        with open(fpn, 'w') as f:
            f.write(m)
        f.close()
        self.objdis.msg2("saved <{}>".format(fpn))

        return True
    #------ guts end ------
    #------ url ------
    def url2name(self, url):
        """given a url, convert to a readable name"""
        netloc = self.url_extract(url)
        if netloc:
            name = ""
            ns = netloc.split(".")
            for value in ns:
                if name:
                    name = "{}.{}".format(name, value)
                else:
                    name = value
            return name
        else:
            return "" 
    def url_extract(self, url, index=1):
        """
        given url, extract specific pieces by index
        setting index=1 returns url domain from 'netloc'
        """
        if url:
            url_split = self.objurl.urlsplit(url)
            return url_split[index]
        else:
            return "" 
    def is_valid_url(self, url):
        """dn ¬
#------¬
def main():¬o we have a valid usable URL?"""
        return self.objval.url(url)
    def count(self, key='size'):
        """
        count all extracted data, original 
        file and (limited) resources and 
        give a total per page
        """
        count = 0
        for d in self.data:
            count += d['size']
        self.length = count
        return self.length
    def count_url(self):
        return self.count(key='url')
    def get_data(self):
        """return all data collected per page"""
        return self.data
        


#------
# name: extract a page of data given url
#------
def extract(url):
    p = Page()
    p.process(url)
    print("({:08})b <{}>".format(p.count(), url))
    p = None


#------
# main 
#------
def main():
    """main cli entry point"""
    urls = ["http://192.168.1.9",
            "http://192.168.1.9/archives",
            "http://seldomlogical.com/qvh.html",
            "http://abc.net.au/news",
            "http://news.ycombinator.com/",
            "http://www.theage.com.au/",
            "http://smh.com.au",
            "http://google.com/ncr",
            "http://google.com.au/",
            "http://guardian.co.uk/"]
    for u in urls:
        extract(u)

#----- main cli entry point ------
if __name__ == "__main__":
    main()


## vim: ff=unix:ts=4:sw=4:tw=78:noai:expandtab
