# -*- coding: utf-8 -*-

def unicode_len(text):
    if isinstance(text, str):
        text = text.decode('utf-8')
    return len(text)
