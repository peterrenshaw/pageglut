#!/usr/bin/env python
# ~*~ encoding: utf-8 ~*~


#======
# name: tools.py
# date: 2016JAN12
# prog: pr
# desc: misc tools used
#======


import os.path        # url2filename
import validators     # is_valid_url
import urllib.parse   # url_extract, url_parse 


DEBUG = False


#======
# name: Display
# date: 2016JAN10
# prog: pr
# desc: basic display object with various
#       methods
#======
class Display(object):
    def __init__(self, is_debug=DEBUG):
        """init"""
        self.is_debug=is_debug
    def msg(self, message):
        """display a message"""
        if self.is_debug:
            print(message)
        else:
            pass
    def msg2(self, message):
        m = "\t{}".format(message)
        return self.msg(m)
    def err(self, message):
        """display an error message"""
        m = "\terror: {}".format(message)
        return self.msg(m)
    def warn(self, message):
        """display a warning message"""
        m = "\twarning: {}".format(message)
        return self.msg(m)


def is_valid_url(url):
    """do we have a valid usable URL?"""
    if url:
        return validators.url(url)
    else:
        return False
def url_repair(base_url, url):
    """fix that broken url"""
    u = urllib.parse.urljoin(base_url, url)
    #print("tools: base_url <{}> url <{}>".format(base_url, url))
    #print("tools.url_repair: u={}".format(u))
    if is_valid_url(u):
        return u
    else:
        return ""
def url_extract(url, index=1):
    """
    given url, extract specific pieces by index
    setting index=1 returns url domain from 'netloc'
    """
    if url:
        url_split = urllib.parse.urlsplit(url)
        return url_split[index]
    else:
        return ""
def url_parse(url, index=2):
    """
    parse url using urlib.parse.urlparse to extract
    filenames. The index defaults to http://domainname/PATH
    """
    if url:
        url_parse = urllib.parse.urlparse(url)
        return url_parse[index]
    else:
        return ""
def url2filename(url):
    """
    given a url, extract filename.ext using url_parse
    """
    netloc = url_parse(url)
    if netloc:
        sfn = os.path.split(netloc)
        # is split filename usable?
        if len(sfn) > 1:
            # ['domain','path'] <== want path
            fn_index = len(sfn) - 1 # max index: get last in list 
            fn = sfn[fn_index]      # get filename
        else:
            fn = sfn
        return fn
    else:
        return ""
def url2name(url, name_unknown='noname'):
    """given a url, convert to a readable name"""
    netloc = url_extract(url)
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
        # don't know a name? make it up
        return name_unknown
def copy_dict(old):
    """
    re-use a dictionary
    """
    new = {}
    for key in old.keys():
        new[key] = old[key]
    return new

#------
# main 
#------
def main():

    print("testing display of messages")
    d = Display()
    d.msg('Message')
    d.msg2('message 2')
    d.err('error message')
    d.warn('warning message')
    d = None

#----- main cli entry point ------
if __name__ == "__main__":
    main()


## vim: ff=unix:ts=4:sw=4:tw=78:noai:expandtab
