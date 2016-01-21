#!/usr/bin/env python
# ~*~ encoding: utf-8 ~*~


import tools


import bs4
import requests
import html5lib


#======
# name: page.py
# date: 2016JAN21
# prog: pr
# desc: request page, extract resources, count the size of a page
#======


#------
# TODO
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
                  objbs=bs4,
                  objtool=tools,
                  objreq=requests,
                  dict_data=PAGE_DATA):
         """initialise Page object"""
         #------ objects ------
         self.objbs = objbs       # beautiful soup extracts from page
         self.objtool = objtool   # access to tools (Display)
         self.objreq = objreq     # request object
         self.objdis = objtool.Display()

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
                 urls = img_url + css_url
                 for u in urls:
                     self.objdis.msg2('url <{}>'.format(u))


                     # --- does url require fixing? ---
                     if not self.objtool.is_valid_url(u):
                         fu = self.objtool.url_repair(page_url, u)
                         self.objdis.warn('fix <{}>'.format(fu))
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
         self.objdis.msg2('get img')
         return self.extract(data, 'image', 'img', 'src')
     def get_css(self, data):
         self.objdis.msg2('get css')
         return self.extract(data, 'css', 'link', 'href')
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
                 else:
                     self.objdis.warn("invalid url <{}>".format(f))
             else:
                 pass

         return urls


def process(url):
    """process a page for resources and find size"""
    p = Page()
    p.request(url)

    rsize = 0
    for resource in p.data['resource']:
        rsize = rsize + int(resource['size'])
    psize =  int(p.data['size'])
    p.data['total'] = psize + rsize

    print("{}\t{}\t\t{}\t<{}>...".format(psize, rsize, (psize + rsize) / 1000, url))

    p = None

#------
# main 
#------
def main():
    URLS = ["http://192.168.1.9", "http://seldomlogical.com", 
            "http://news.ycombinator.com", "http://guardian.co.uk",
            "http://theage.com.au","http://buzzfeed.com",
            "http://kittenskittenskittens.tumblr.com"]

    URLS2 = ['https://twitter.com/davewiner/status/689672660675121152', 
             'http://scripting.com/liveblog/users/davewiner/2016/01/20/0900.html',
             'https://www.facebook.com/dave.winer.12/posts/409275095946568?comment_id=409418535932224&comment_tracking=%7B%22tn%22%3A%22R1%22%7D&pnref=story',
             'https://medium.com/@davewiner/anywhere-but-medium-5450cb19f2c1#.2gv2klp7h']


    print("page\tresource\ttotal\t\turl")
    print("(b)\t(b)\t\t(Kb)")
    print("----------------------------------------------------------")
    for url in URLS2:
        process(url)
    print("-----------------------------------------------------------")


#----- main cli entry point ------
if __name__ == "__main__":
    main()


## vim: ff=unix:ts=4:sw=4:tw=78:noai:expandtab
