# -*- coding: utf-8 -*-

from MySQLdb import escape_string

def to_ascii(text):
    if isinstance(text, unicode):
        text = text.encode('utf-8')
    return text

def unicode_len(text):
    if isinstance(text, str):
        text = text.decode('utf-8')
    return len(text)

def escape(text):
    if isinstance(text, unicode):
        text = text.encode('utf-8')
    if text:
        return escape_string(text).decode('utf-8')
    return None

