#!/usr/bin/env python3
# ~*~ encoding: utf-8 ~*~


#=======
#                                  __      __ 
#    ____  ____ _____ ____  ____ _/ /_  __/ /_
#   / __ \/ __ `/ __ `/ _ \/ __ `/ / / / / __/
#  / /_/ / /_/ / /_/ /  __/ /_/ / / /_/ / /_  
# / .___/\__,_/\__, /\___/\__, /_/\__,_/\__/  
#/_/          /____/     /____/               
#
# This file is part of Page Glut.
#
# Page Glut is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Page Glut is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Page Glut.  If not, see <http://www.gnu.org/licenses/gpl-3.0.txt>.
#
# name: pageglut.py
# date: 2018DEC31
#       2016NOV12
# prog: pr
# desc: Page Gluts: read docs/ABOUT.txt
# sorc: BS4:       <https://github.com/newvem/beautifulsoup>
#       Decorator: <https://pypi.org/simple/decorator/>
#       encodings: <https://github.com/gsnedders/python-webencodings>
#======


import argparse


import tools


import bs4
import requests
import html5lib


#======
# name: pageglut.py
# date: 2016DEC23
#       2016JAN21
# prog: pr
# desc: request page, extract resources, count the size of a page
# todo: javascript request.
#======


#------
# TODO
#      * Page has JS?
#      - grab the size of the JS loaded
#     
#      * Page queries URL
#      - list of URLS obtained
#      - when looping thru urls
#      + check if url is requested by page?
#      + ie: image, css file NOT .html file found as link in page
#      + another hint is via content-type
#
#      * recheck resources for broken urls and fix
#      - sometimes resource links found on pages are relative
#      - when I do a check if they are valid, rel links will break
#      - fix them, then re-try
#
#------


#------
# name: PAGE_DATA
# date: 2016JAN21
# prog: pr
# desc: external structure that can be changed independent 
#       of objects if we want to capture more/less. Remove
#       keys at your own risk. 
#------
PAGE_DATA = {'name': '',        # page name 
             'rtype': '',       # page resource type ['text|img']
             'text': '',        # page content when type is text
             'url': '',         # page url
             'header': {},      # returned header
             'size': 0,         # size of page
             'totalsize': 0,    # total of page and resources
             'resource': []}    # list of text or image called by page

#======
# name: Page
# date: 2016JAN21
# prog: pr
# desc: class Page encapsulate request, extract and enumerate data
#======
class Page(object):
     def __init__(self,
                  debug,
                  objbs=bs4,
                  objtool=tools,
                  objreq=requests,
                  dict_data=PAGE_DATA):
         """initialise Page object"""
         self.is_debug = debug
         #------ objects ------
         self.objbs = objbs       # beautiful soup extracts from page
         self.objtool = objtool   # access to tools (Display)
         self.objreq = objreq     # request object
         self.objdis = objtool.Display(self.is_debug)

         #------ structure ------ 
         self.store = self.objtool.copy_dict(dict_data)
         self.data = dict_data
         
     def request(self, page_url):
         """first pass of url, download and extract header"""
         self.objdis.msg('request <{}>'.format(page_url))
         status = self.objtool.is_valid_url(page_url)
         if status:
             self.objdis.msg2('url ok')
            
             #------ request start ------
             r = self.objreq.get(page_url)
             if (r.status_code == self.objreq.codes.ok):
                 self.objdis.msg2('status {}'.format(r.status_code))
               
                 # hard coded 
                 self.setd('rtype', 'text')
                 name = "root-{}".format(self.objtool.url2name(page_url))
                 self.setd('name', name)

                 # determined by header
                 self.setd('url', page_url)
                 self.setd('header', r.headers)
                 self.setd('text', r.text)
                 self.set_size(r)

                 #------ extract start (resources from page) ------
                 img_url = self.get_image(r.text)
                 css_url = self.get_css(r.text)
                 js_url = self.get_js(r.text)
                 
                 urls = img_url + css_url + js_url
                 for u in urls:
                     self.objdis.msg2('url <{}>'.format(u))


                     # --- does url require fixing? ---
                     if not self.objtool.is_valid_url(u):
                         fu = self.objtool.url_repair(page_url, u)
                         if fu:
                             self.objdis.warn('fixed url <{}>'.format(fu))
                         else:
                             self.objdis.err("skip broken url <{}>".format(u))
                             break
                     else:
                         fu = u
                         self.objdis.msg2("ok")
                     
                     # --- request resource ---
                     resource = self.objreq.get(fu)
                     self.objdis.msg2("status {}".format(resource.status_code))
 
                     store = self.objtool.copy_dict(self.store)
                     store['url'] = fu
                     res_name = "res-{}".format(self.objtool.url2filename(fu))
                     store['name'] = res_name

                     #--- headers start ---
                     store['header'] = resource.headers
                     # size
                     if 'content-type' in resource.headers:
                         if resource.headers['content-type'] == 'text/html':
                             store['text'] = resource.text
                         else:
                             self.objdis.warn('content type not text')
                     else:
                         self.objdis.warn('content type not found')

                     # --- size ---
                     if 'content-length' in resource.headers:
                         store['size'] = resource.headers['content-length']
                         self.objdis.msg2("size {}".format(store['size']))
                     else:
                         self.objdis.warn("header.'content-length' no content size found")
                     #--- headers end ---
                     self.data['resource'].append(store)

                     resource = None

                 #------ extract end ------

             else:
                 self.objdis.warn('request status {}'.format(r.status_code))
             #------ request end ------

             r = None              
         else:
             self.objdis.warn('url failure')

         return status
     #------ set/get start ------
     def set_size(self, headers):
         """
         set the size of the page either by header content length 
         or header text size, return T or F
         """
         if 'content-length' in headers:
             # size found in reported header length
             return self.setd('size', headers.header['content-length'])
         else:
             # size found in length of header text
             return self.setd('size', len(headers.text))
     def setd(self, key, value):
         """set data by key and value, return T or F"""
         if key in self.data:
             self.data[key] = value
             return True
         else:
             return False
     def get_image(self, data):
         """search for image resources in a page of data"""
         # <img src="s.gif" height="10" width="0">
         self.objdis.msg2('get img')
         return self.extract(data, 'image', 'img', 'src')
     def get_css(self, data):
         # <link rel="stylesheet" type="text/css" href="news.css?AMTnWwphWLGKuspwrcEL">
         self.objdis.msg2('get css')
         return self.extract(data, 'css', 'link', 'href')
     def get_js(self, data):
         # <script type='text/javascript' src='hn.js?AMTnWwphWLGKuspwrcEL'></script></html>
         self.objdis.msg2('get js')
         return self.extract(data, 'javascript', 'script', 'src')
     #------ get/set end ------
     def extract(self, data, label, key1, key2):
         self.objdis.msg2("extract")
         self.objdis.msg2("ex '{}' '{}' '{}'".format(label, key1, key2))

         urls = []

         found = self.objbs.BeautifulSoup(data, "html5lib")
         for item in found.find_all(key1):
             if item:
                 if key2:
                     f = item.get(key2)
                 else:
                     f = item
                 if self.objtool.is_valid_url(f):
                     urls.append(f)
                 elif f:
                     urls.append(f)
                     self.objdis.warn("problem url, needs fixing <{}>".format(f))
                 else:
                     self.objdis.warn("invalid url <{}>".format(f))
             else:
                 pass

         self.objdis.msg2("extract {} <{}>".format(label, urls))
         return urls


#-------
# name: process
# date: 2016DEC23
# prog: pr
# desc: wrapper for Page object to process one html index page at a time
#-------
def process(url, debug):
    """process a page for resources and find size"""
    p = Page(debug)
    p.request(url)

    rsize = 0
    for resource in p.data['resource']:
        rsize = rsize + int(resource['size'])
    psize =  int(p.data['size'])
    p.data['total'] = psize + rsize

    print("{}\t{}\t\t{}\t\t<{}>...".format(psize, rsize, (psize + rsize) / 1000, url))

    p = None


#-------
# name: display
# date: 2016DEC23
# prog: pr
# desc: basic cli display of a page resources used
#-------
def display(url, debug):
    """show output"""
    print("page\tresource\ttotal\t\turl")
    print("(b)\t(b)\t\t(Kb)")
    print("----------------------------------------------------------")
    process(url, debug)
    print("-----------------------------------------------------------")


#------
# main 
#------
def main():
    parser = argparse.ArgumentParser(description="calculate page sizes")
    parser.add_argument("-u","--url", help="URL to inspect")
    parser.add_argument("-v","--verbose",action="store_true",help="verbosity of debug messages")
    
    options = parser.parse_args()

    if options.verbose: debug = True
    else: debug = tools.DEBUG

    if options.url:
        display(options.url, debug)



#----- main cli entry point ------
if __name__ == "__main__":
    main()


## vim: ff=unix:ts=4:sw=4:tw=78:noai:expandtab

