#!/usr/bin/env python
# ~*~ encoding: utf-8 ~*~


import tools


import bs4
import requests
import html5lib


#------ 
# name: Resource
# date: 2016JAN12
# prog: pr
# desc: storage class for Page resource data
#------
class Resource(object):
    def __init__(self):
        self._name = ""     # unique label
        self._text = ""     # content of resource (text only)
        self._url = ""      # url of resource
        self._header = {}   # response header
        self._size = 0      # size in kb
        self._resource = []  # list of internal resources per page
        self._rtype = ""
    def clear(self):
        self._name = ""     # unique label
        self._text = ""     # content of resource (text only)
        self._url = ""      # url of resource
        self._header = {}   # response header
        self._size = 0      # size in kb
        self._resource = []  # list of internal resources per page
        self._rtype = ""
        return True 
    def getname(self):
        return self._name
    def setname(self, name):
        self._name = name
    def gettext(self):
        return self._text
    def settext(self, text):
        self._text = text
    def geturl(self):
        return self._url
    def seturl(self, url):
        self._url = url
    def getheader(self):
        return self._header
    def setheader(self, header):
        self._header = header
    def getsize(self):
        return self._size
    def setsize(self, size):
        self._size = size
    def getresource(self):
        return self._resource
    def setresource(self, resource):
        self._resource = resource
    def getrtype(self):
        return self._rtype
    def setrtype(self, rtype):
        self._rtype = rtype
    name = property(getname, setname, None, None)
    text = property(gettext, settext, None, None)
    url = property(geturl, seturl, None, None)
    header = property(getheader, setheader, None, None)
    size = property(getsize, setsize, None, None)
    rtype = property(getrtype, setrtype, None, None)
    resource = property(getresource, setresource, None, None)
objr = Resource()


data = {'name':'', 'rtype': '', 'text':'', 'url':'', 
        'header':{}, 'size': 0, 'resource': []}

class Page(object):
    def __init__(self, objtool=tools,
                       objreq=requests,
                       objdat=objr,
                       objres=data,
                       objbs=bs4):
        """initialise object"""
        #------ obj ------
        self.objtool = objtool
        self.objdis = objtool.Display()
        self.objreq = objreq
        self.objdat = objdat
        self.objres = objres
        self.objbs = objbs
        #------ data ------
        self.urls = []
        self.resources = []
        self.data = self.objdat
    def request(self, purl):
        """first pass of url, download, extract header"""
        if purl:
            self.objdis.msg("request")
            if self.objtool.is_valid_url(purl):
                self.objdis.msg2("url ok")

                r = self.objreq.get(purl)

                # fill in the resource
                self.objdat.text = r.text
                self.objdat.header = r.headers
                self.objdat.url = purl
                self.objdat.rtype = "page"
                self.objdat.name = self.objtool.url2name(purl)
               
                # size == header content length OR len(header text) 
                content_length = self.get_header(r, 'content-length')
                if content_length:
                    self.objdat.size = content_length
                else:
                    self.objdat.size = len(r.text)

                # lets extract image resource from text
                url_img = self.get_img(r.text)
                url_css = self.get_css(r.text)

                u = url_img + url_css
                for data in u:
                    name = data['key'] 
                    u = data['value']
                    print("name '{}'".format(name))


                    # url need fixing?
                    if not self.objtool.is_valid_url(data['value']):
                        fu = self.objtool.url_repair(purl, u)
                        self.objdis.msg2("fixed url={}".format(u))
                    else:
                        fu = data['value']

                    # url should be fixed, if not log
                    if self.objtool.is_valid_url(fu): 
                        self.objdis.msg2("extract {} <{}>".format(name, fu))
                        resource = self.objreq.get(fu)
                        
                        o = self.objres 
                        o['text'] = "" #resource.text -- image!
                        o['header'] = resource.headers
                        o['url'] = fu
                        o['rtype'] = name
                        o['name'] = self.objtool.url2name(fu)

                        #print("o: '{}' ({}) <{}>".format(o.name, o.rtype, o.url))
                        #keys = o.keys()
                        #for key in keys:
                        #    print("k={}".format(key))

                        self.resources.append(o)
                        o = None

                    else:
                        self.objdis.warn("broken url <{}>".format(fu))
               
                #print("resources ({})".format(len(self.resources)))
                #for resource in self.resources:
                #    print("name={}".format(resource.name))
                #    print("url  <{}>".format(resource.url))
 
                self.objdat.resource = self.resources
                r = None
                return True
            else:
                return False
        else:
            return False
    def get_data(self):
        return self.data
    def get_header(self, header, label):
        if header:
            if label in header:
                return header[label]
        return False
    def get_img(self, data):
        self.objdis.msg("get image")
        return self.get(data=data, label='img', key1='img', key2='src')
    def get_css(self, data):
        self.objdis.msg("get image")
        return self.get(data=data, label='css', key1='link', key2='href')
    def get(self, data, label, key1, key2):
        self.objdis.msg("get")
        self.objdis.msg2("{}: {} {}".format(label, key1, key2))

        urls = []
        found = self.objbs.BeautifulSoup(data, "html5lib")
        for item in found.find_all(key1):
            if item:
                if key2:
                    f = item.get(key2)
                else:
                    f = item
                urls.append({'key': label, 'value': f})
            else:
                pass
        return urls
#------
# main 
#------
def main():
    URL = "http://192.168.1.9"

    p = Page()
    p.request(URL)

    d = p.get_data()
    print("name={}".format(d.name))
    print("url=<{}>".format(d.url))
    print("headers={}".format(d.header))
    print("type={}".format(d.rtype))
    print("size={}".format(d.size))
    print("resources")
    resources = d.resource
    for resource in resources:
        print("name='{}'".format(resource['name']))
        print("url=<{}>".format(resource['url']))
        print("header=''".format(resource['header']))



    p = None

#----- main cli entry point ------
if __name__ == "__main__":
    main()


## vim: ff=unix:ts=4:sw=4:tw=78:noai:expandtab
