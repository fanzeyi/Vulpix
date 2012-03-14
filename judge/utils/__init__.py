# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: judge/utils/__init__.py
# CREATED: 02:09:10 15/03/2012
# MODIFIED: 02:10:04 15/03/2012

def _len(text):
    if isinstance(text, str):
        text = text.decode('utf-8')
    return len(text)
