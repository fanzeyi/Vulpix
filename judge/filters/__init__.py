# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: judge/filters/__init__.py
# CREATED: 01:48:10 08/03/2012
# MODIFIED: 04:06:44 09/03/2012
# DESCRIPTION: jinja2 filters

def avatar_img(link, size = 45):
    return "<img src=\"%s\" width=\"%d\" height=\"%d\" />" % (link, size, size)

filters = {
    'avatar_img' : avatar_img, 
}
